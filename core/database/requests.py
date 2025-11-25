from sqlalchemy import select, update, delete, BigInteger, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, aliased


from core.database.models import User, Profile, Notification
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
        return user.profile.notifications, user.profile.qwery

async def edit_notif_by_tg_id(
        user_tg_id: int,
):
    async with LocalSession() as session:
        stmt = (
            select(User)
            .where(User.user_tg_id == user_tg_id)
            .options(selectinload(User.profile))
            .limit(1)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user.profile.notifications:
            user.profile.notifications = False
        else:
            user.profile.notifications = True
        await session.commit()

async def edit_query_by_tg_id(
        user_tg_id: int,
):
    async with LocalSession() as session:
        stmt = (
            select(User)
            .where(User.user_tg_id == user_tg_id)
            .options(selectinload(User.profile))
            .limit(1)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user.profile.qwery:
            user.profile.qwery = False
        else:
            user.profile.qwery = True
        await session.commit()


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
                .where(Profile.qwery.is_(True))
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
            return False  # Пользователь не найден


        # Создаём запись
        new_notification = Notification(
            user_id=user_id,
            health=query,
            kp=kp
        )
        session.add(new_notification)
        await session.commit()
        return True