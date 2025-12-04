import csv
import io
from uuid import UUID
from fastapi import Response

from app.schemas.quiz_attempt import QuizAttemptsList, QuizAttemptSchema
from app.unit_of_work import UnitOfWork
from app.exceptions import UnauthorizedQuizAction, QuizNotFound
from app.enums import Roles
from app.utils import LoggerUtil


class ExportService:
    def __init__(self):
        self.logger_util = LoggerUtil()

    async def _check_company_admin_access(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_id: UUID,
    ) -> None:
        memberships, _ = await uow.membership.read(
            field="user_id", value=current_user_id, offset=0, limit=100
        )

        if any(
                m.company_id == company_id
                and m.role in {Roles.ADMIN, Roles.OWNER}
                and m.is_active
                for m in memberships
        ):
            return

        raise UnauthorizedQuizAction

    async def _get_user_quiz_results(
            self,
            uow: UnitOfWork,
            user_id: UUID,
            quiz_id: UUID | None = None,
    ) -> QuizAttemptsList:
        quiz_attempts, total = await uow.quiz_attempts.read(
            field="user_id",
            value=user_id,
            offset=0,
            limit=10000,
            load_relationships=[
                "user_answers",
                "user",
                "company",
                "quiz",
                "quiz.questions",
                "quiz.questions.answer_options",
            ]
        )

        if quiz_id:
            quiz_attempts = [qa for qa in quiz_attempts if qa.quiz_id == quiz_id]
            total = len(quiz_attempts)

        quiz_attempts_schemas = [
            QuizAttemptSchema.model_validate(quiz_attempt)
            for quiz_attempt in quiz_attempts
        ]

        return QuizAttemptsList(
            quiz_attempts=quiz_attempts_schemas,
            total=total,
        )

    async def _get_company_quiz_results(
            self,
            uow: UnitOfWork,
            company_id: UUID,
            quiz_id: UUID | None = None,
            user_id: UUID | None = None,
    ) -> QuizAttemptsList:
        quiz_attempts, total = await uow.quiz_attempts.read(
            field="company_id",
            value=company_id,
            offset=0,
            limit=10000,
            load_relationships=[
                "user_answers",
                "user",
                "company",
                "quiz",
                "quiz.questions",
                "quiz.questions.answer_options",
            ]
        )

        if quiz_id:
            quiz_attempts = [qa for qa in quiz_attempts if qa.quiz_id == quiz_id]

        if user_id:
            quiz_attempts = [qa for qa in quiz_attempts if qa.user_id == user_id]

        total = len(quiz_attempts)

        quiz_attempts_schemas = [
            QuizAttemptSchema.model_validate(quiz_attempt)
            for quiz_attempt in quiz_attempts
        ]

        return QuizAttemptsList(
            quiz_attempts=quiz_attempts_schemas,
            total=total,
        )

    def _to_json(self, data: QuizAttemptsList) -> str:
        return data.model_dump_json(indent=2, exclude_none=True)

    def _to_csv(self, data: QuizAttemptsList) -> str:
        output = io.StringIO()
        fieldnames = [
            "quiz_attempt_id",
            "user_id",
            "user_name",
            "user_surname",
            "user_nickname",
            "user_email",
            "company_id",
            "company_name",
            "quiz_id",
            "quiz_title",
            "correct_answers",
            "total_questions",
            "score_percentage",
            "created_at",
            "updated_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for attempt in data.quiz_attempts:
            score_percentage = (
                round((attempt.correct_answers / attempt.total_questions) * 100, 2)
                if attempt.total_questions > 0
                else 0
            )

            writer.writerow(
                {
                    "quiz_attempt_id": str(attempt.id),
                    "user_id": str(attempt.user_id),
                    "user_name": attempt.user.name if attempt.user else "",
                    "user_surname": attempt.user.surname if attempt.user else "",
                    "user_nickname": attempt.user.nickname if attempt.user else "",
                    "user_email": attempt.user.email if attempt.user else "",
                    "company_id": str(attempt.company_id),
                    "company_name": attempt.company.name if attempt.company else "",
                    "quiz_id": str(attempt.quiz_id),
                    "quiz_title": attempt.quiz.title if attempt.quiz else "",
                    "correct_answers": attempt.correct_answers,
                    "total_questions": attempt.total_questions,
                    "score_percentage": score_percentage,
                    "created_at": (
                        attempt.created_at.isoformat() if attempt.created_at else ""
                    ),
                    "updated_at": (
                        attempt.updated_at.isoformat() if attempt.updated_at else ""
                    ),
                }
            )

        return output.getvalue()

    def _create_response(
            self,
            data: QuizAttemptsList,
            export_type: str,
            filename_prefix: str,
    ) -> Response:
        if export_type == "csv":
            content = self._to_csv(data)
            media_type = "text/csv"
        else:
            content = self._to_json(data)
            media_type = "application/json"

        filename = f"{filename_prefix}.{export_type}"

        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    async def export_user_results(
            self,
            uow: UnitOfWork,
            user_id: UUID,
            quiz_id: UUID | None,
            export_type: str,
    ) -> Response:
        data = await self._get_user_quiz_results(uow, user_id, quiz_id)

        filename_prefix = f"my_results_quiz_{quiz_id}" if quiz_id else "my_results_all"

        return self._create_response(data, export_type, filename_prefix)

    async def export_company_user_results(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_id: UUID,
            user_id: UUID,
            quiz_id: UUID | None,
            export_type: str,
    ) -> Response:
        await self._check_company_admin_access(uow, current_user_id, company_id)

        data = await self._get_company_quiz_results(
            uow, company_id, quiz_id, user_id
        )

        filename_prefix = (
            f"user_{user_id}_quiz_{quiz_id}"
            if quiz_id
            else f"user_{user_id}_all"
        )

        return self._create_response(data, export_type, filename_prefix)

    async def export_company_all_results(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_id: UUID,
            quiz_id: UUID | None,
            export_type: str,
    ) -> Response:
        await self._check_company_admin_access(uow, current_user_id, company_id)

        data = await self._get_company_quiz_results(uow, company_id, quiz_id)

        filename_prefix = (
            f"company_{company_id}_quiz_{quiz_id}"
            if quiz_id
            else f"company_{company_id}_all"
        )

        return self._create_response(data, export_type, filename_prefix)

    async def export_company_quiz_results(
            self,
            uow: UnitOfWork,
            current_user_id: UUID,
            company_id: UUID,
            quiz_id: UUID,
            export_type: str,
    ) -> Response:
        await self._check_company_admin_access(uow, current_user_id, company_id)

        quiz, _ = await uow.quizzes.read(field="id", value=quiz_id, offset=0, limit=1)
        if not quiz or quiz[0].company_id != company_id:
            raise QuizNotFound

        data = await self._get_company_quiz_results(uow, company_id, quiz_id)

        filename_prefix = f"quiz_{quiz_id}_results"

        return self._create_response(data, export_type, filename_prefix)
