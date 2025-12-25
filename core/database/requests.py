from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload


from core.database.models import User, Profile, Health
from core.database.session import LocalSession

async def create_user_with_profile(user_tg_id: int, username: str) -> bool:
    async with LocalSession() as session:
        try:
            user = User(user_tg_id=user_tg_id, username=username)
            session.add(user)
            profile = Profile(user=user)
            session.add(profile)

            await session.commit()
            return True
        except IntegrityError:
            return False


async def get_profile_by_tg_id(
        user_tg_id: int,
) -> (bool, bool):
    async with LocalSession() as session:
        stmt = (
            select(User)
            .where(User.user_tg_id == user_tg_id)
            .options(selectinload(User.profile))
            .limit(1)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user.profile.notifications, user.profile.query


async def toggle_profile_flag(
    user_tg_id: int,
    field: str,
):
    async with LocalSession() as session:
        stmt = (
            select(User)
            .where(User.user_tg_id == user_tg_id)
            .options(selectinload(User.profile))
        )

        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.profile:
            return False

        if not hasattr(user.profile, field):
            raise AttributeError(f"Profile has no field '{field}'")

        current_value = getattr(user.profile, field)
        setattr(user.profile, field, not current_value)

        await session.commit()
        return True


async def get_user_ids(for_notifications: bool = False, for_qwery: bool = False):
    async with LocalSession() as session:
        if for_notifications:
            stmt = (
                select(User.user_tg_id)
                .join(Profile, User.id == Profile.user_id)
                .where(Profile.notifications.is_(True))
            )
        if for_qwery:
            stmt = (
                select(User.user_tg_id)
                .join(Profile, User.id == Profile.user_id)
                .where(Profile.query.is_(True))
            )
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_all_user_ids():
    async with LocalSession() as session:
        stmt = (
            select(User.user_tg_id)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

async def update_query_by_tg_id(
        user_tg_id: int,
        query: str,
        kp,
):
    async with LocalSession() as session:
        result = await session.execute(
            select(User.id).where(User.user_tg_id == user_tg_id)
        )
        user_id = result.scalar_one_or_none()

        if user_id is None:
            return False


        # Создаём запись
        new_notification = Health(
            user_id=user_id,
            health=query,
            kp=kp
        )
        session.add(new_notification)
        await session.commit()
        return True