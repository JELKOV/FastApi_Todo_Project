"""
사용자 서비스 레이어

사용자 관련 비즈니스 로직을 처리합니다.
데이터베이스 작업과 에러 핸들링을 담당합니다.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
from fastapi import HTTPException, status
from app.users.domain.models import User
from app.users.domain.entities import UserCreate, UserUpdate, UserResponse


class UserService:
    """
    사용자 서비스 클래스

    사용자 관련 CRUD 작업과 비즈니스 로직을 처리합니다.
    """

    def __init__(self, db: Session):
        """
        UserService 초기화

        Args:
            db: SQLAlchemy 데이터베이스 세션
        """
        self.db = db

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        새 사용자 생성

        Args:
            user_data: 사용자 생성 데이터

        Returns:
            UserResponse: 생성된 사용자 정보

        Raises:
            HTTPException: 데이터베이스 오류 시
        """
        try:
            # 비밀번호 해시화 (실제 프로덕션에서는 bcrypt 사용 권장)
            hashed_password = self._hash_password(user_data.password)

            # 새 사용자 객체 생성
            user = User(
                username=user_data.username,
                email=user_data.email,
                password=hashed_password
            )

            # 데이터베이스에 저장
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            # Pydantic 모델로 변환하여 반환
            return UserResponse.model_validate(user)

        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)

            # 중복 키 오류 처리
            if "23505" in error_msg:  # unique_violation
                if "username" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="이미 존재하는 사용자명입니다"
                    )
                elif "email" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="이미 존재하는 이메일입니다"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="중복된 데이터입니다"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="데이터 무결성 오류가 발생했습니다"
                )

        except (DataError, ValueError) as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="잘못된 데이터 형식입니다"
            )

        except OperationalError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 오류가 발생했습니다"
            )

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="서버 내부 오류가 발생했습니다"
            )

    def get_user_by_id(self, user_id: int) -> UserResponse:
        """
        ID로 사용자 조회

        Args:
            user_id: 사용자 ID

        Returns:
            UserResponse: 사용자 정보

        Raises:
            HTTPException: 사용자를 찾을 수 없을 때
        """
        user = self.db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        return UserResponse.model_validate(user)

    def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """
        사용자명으로 사용자 조회

        Args:
            username: 사용자명

        Returns:
            Optional[UserResponse]: 사용자 정보 또는 None
        """
        user = self.db.query(User).filter(User.username == username).first()
        if user:
            return UserResponse.model_validate(user)
        return None

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        이메일로 사용자 조회

        Args:
            email: 이메일 주소

        Returns:
            Optional[UserResponse]: 사용자 정보 또는 None
        """
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            return UserResponse.model_validate(user)
        return None

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """
        사용자 정보 수정

        Args:
            user_id: 사용자 ID
            user_data: 수정할 사용자 데이터

        Returns:
            UserResponse: 수정된 사용자 정보

        Raises:
            HTTPException: 사용자를 찾을 수 없거나 데이터 오류 시
        """
        try:
            # 기존 사용자 조회
            user = self.db.get(User, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다"
                )

            # 수정할 필드만 업데이트
            update_data = user_data.model_dump(exclude_unset=True)

            if 'username' in update_data:
                user.username = update_data['username']
            if 'email' in update_data:
                user.email = update_data['email']
            if 'password' in update_data:
                user.password = self._hash_password(update_data['password'])

            # 데이터베이스에 저장
            self.db.commit()
            self.db.refresh(user)

            return UserResponse.model_validate(user)

        except HTTPException:
            self.db.rollback()
            raise
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)

            if "23505" in error_msg:  # unique_violation
                if "username" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="이미 존재하는 사용자명입니다"
                    )
                elif "email" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="이미 존재하는 이메일입니다"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="데이터 무결성 오류가 발생했습니다"
                )
        except (DataError, ValueError):
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="잘못된 데이터 형식입니다"
            )
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="서버 내부 오류가 발생했습니다"
            )

    def delete_user(self, user_id: int) -> bool:
        """
        사용자 삭제

        Args:
            user_id: 사용자 ID

        Returns:
            bool: 삭제 성공 여부

        Raises:
            HTTPException: 사용자를 찾을 수 없을 때
        """
        try:
            user = self.db.get(User, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다"
                )

            self.db.delete(user)
            self.db.commit()
            return True

        except HTTPException:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="서버 내부 오류가 발생했습니다"
            )

    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        사용자 목록 조회

        Args:
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수

        Returns:
            List[UserResponse]: 사용자 목록
        """
        users = self.db.query(User).offset(skip).limit(limit).all()
        return [UserResponse.model_validate(user) for user in users]

    def _hash_password(self, password: str) -> str:
        """
        비밀번호 해시화

        Args:
            password: 원본 비밀번호

        Returns:
            str: 해시된 비밀번호
        """
        # 실제 프로덕션에서는 passlib의 bcrypt 사용 권장
        # 여기서는 간단한 예시로 구현
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        비밀번호 검증

        Args:
            plain_password: 입력된 비밀번호
            hashed_password: 저장된 해시 비밀번호

        Returns:
            bool: 비밀번호 일치 여부
        """
        return self._hash_password(plain_password) == hashed_password
