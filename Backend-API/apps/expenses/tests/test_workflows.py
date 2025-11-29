from decimal import Decimal
from datetime import date

from rest_framework.test import APITestCase, APIClient

from apps.users.models import User
from apps.expenses.models import ExpenseType, Expense, ExpensePayment


class ExpenseWorkflowAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            name="Test",
            last_name="User",
            password="pass1234",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.expense_type = ExpenseType(
            code="HON",
            name="Honorarios",
            retention_percent=Decimal("2.50"),
            retention_minimum_amount=Decimal("100.00"),
        )
        self.expense_type.save(user=self.user)

    def _build_expense(self, amount=Decimal("800.00"), vat=Decimal("200.00")) -> Expense:
        expense = Expense(
            expense_type=self.expense_type,
            expense_date=date(2025, 1, 10),
            concept="Servicio profesional",
            net_amount_primary=amount,
            vat_amount_primary=vat,
        )
        expense.save(user=self.user)
        return expense

    def _build_payment(self, total=Decimal("1000.00")) -> ExpensePayment:
        payment = ExpensePayment(
            payment_date=date(2025, 1, 15),
            person_legacy_id=10,
            total_amount=total,
        )
        payment.save(user=self.user)
        return payment

    def test_approve_expense_workflow(self):
        expense = self._build_expense()
        url = f"/api/v1/expenses/records/{expense.id}/approve/"
        response = self.client.post(url, {"notes": "Listo para pagar"}, format="json")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status_label"], Expense.Status.APPROVED)

        expense.refresh_from_db()
        self.assertIsNotNone(expense.approved_at)
        self.assertEqual(expense.approved_by, self.user)
        self.assertEqual(expense.approval_notes, "Listo para pagar")

    def test_partial_allocation_and_auto_retention(self):
        expense = self._build_expense()
        payment = self._build_payment()
        url = f"/api/v1/expenses/payments/{payment.id}/allocations/"

        first_payload = {"expense": expense.id, "amount": "400.00"}
        resp1 = self.client.post(url, first_payload, format="json")
        self.assertEqual(resp1.status_code, 200)

        expense.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(expense.amount_paid, Decimal("400.00"))
        self.assertEqual(expense.status_label, Expense.Status.APPROVED)
        self.assertEqual(payment.retention_total_amount, Decimal("10.00"))

        second_payload = {"expense": expense.id, "amount": "600.00"}
        resp2 = self.client.post(url, second_payload, format="json")
        self.assertEqual(resp2.status_code, 200)

        expense.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(expense.status_label, Expense.Status.PAID)
        self.assertEqual(expense.amount_paid, Decimal("1000.00"))
        self.assertEqual(payment.retention_total_amount, Decimal("25.00"))

    def test_allocation_cannot_exceed_outstanding(self):
        expense = self._build_expense()
        payment = self._build_payment()
        url = f"/api/v1/expenses/payments/{payment.id}/allocations/"

        payload = {"expense": expense.id, "amount": "1500.00"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())