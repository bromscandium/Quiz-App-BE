import json
import csv
import io
from uuid import UUID
from fastapi import Response

from app.schemas.quiz_attempt import QuizAttemptsList, QuizAttemptSchema
from app.unit_of_work import UnitOfWork
from app.exceptions import UnauthorizedCompanyOwner, QuizNotFound
from app.permissions import check_owner_permission
from app.utils import LoggerUtil


class ExportService:
    def __init__(self):
        self.logger_util = LoggerUtil()

    async def _get_quiz_results(
        self,
        uow: UnitOfWork,
        company_id: UUID | None,
        quiz_id: UUID | None,
    ) -> QuizAttemptsList:
        field = "quiz_id" if quiz_id else "company_id"
        value = quiz_id if quiz_id else company_id

        quiz_attempts, total = await uow.quiz_attempts.read(
            field=field,
            value=value,
            offset=0,
            limit=1000,
            load_relationships=[
                "user_answers",
                "user",
                "company",
                "company.owner",
                "quiz",
                "quiz.questions",
                "quiz.questions.answer_options",
            ],
        )

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

    async def export_quiz_results(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        company_id: UUID | None,
        quiz_id: UUID | None,
        export_type: str,
    ) -> Response:
        if not await check_owner_permission(current_user_id, uow, company_id):
            self.logger_util.info("Owner not authorized for export")
            raise UnauthorizedCompanyOwner

        if quiz_id:
            quiz, _ = await uow.quizzes.read(
                field="id",
                value=quiz_id,
                offset=0,
                limit=1,
            )
            if not quiz:
                self.logger_util.info("Quiz not found")
                raise QuizNotFound

        data = await self._get_quiz_results(uow, company_id, quiz_id)

        if export_type == "csv":
            content = self._to_csv(data)
            media_type = "text/csv"
        else:
            content = self._to_json(data)
            media_type = "application/json"

        filename = f"quiz_{quiz_id if quiz_id else company_id}_results.{export_type}"

        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
