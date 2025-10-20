import asyncio
from uuid import uuid4

from app.infrastructure.database.connection import initialize_database, create_database_tables, get_database_session
from app.infrastructure.repositories.job_description_repository import JobDescriptionRepository
from app.domain.entities.job_description import JobDescription, JobDescriptionMetadata, JobDescriptionSource


async def main():
    initialize_database()
    await create_database_tables()

    async with get_database_session() as session:
        repo = JobDescriptionRepository(session)
        user_id = uuid4()
        jd = JobDescription.create(
            user_id=user_id,
            title="Smoke Job",
            company="SmokeCorp",
            description="Smoke test",
            requirements=["x"],
            benefits=[],
            source=JobDescriptionSource.MANUAL,
            metadata=JobDescriptionMetadata.create_empty(),
        )

        created = await repo.create(jd)
        print("created id", created.id)

        fetched = await repo.get_by_id(jd.id)
        print("fetched", fetched.title if fetched else None)

        count = await repo.count_by_user_id(user_id)
        print("count", count)

        await repo.delete(jd.id)
        print("deleted")


if __name__ == '__main__':
    asyncio.run(main())
