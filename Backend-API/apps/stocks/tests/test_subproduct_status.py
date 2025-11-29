from decimal import Decimal
from django.test import TestCase
from apps.tests.factories import create_user, create_category, create_product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models.stock_subproduct_model import SubproductStock
from apps.stocks.models.stock_event_model import StockEvent

class SubproductStockStatusTestCase(TestCase):
    def setUp(self):
        self.user = create_user(username='testuser', email='test@example.com')
        self.category = create_category(name='CatTest', user=self.user)
        self.product = create_product(self.category, user=self.user, name='ProdTest')

    def test_create_subproduct_with_initial_stock_gt_zero_sets_status_true(self):
        subp = Subproduct.objects.create(
            parent=self.product,
            brand='TestBrand',
            number_coil=123,
            initial_stock_quantity=Decimal('105.00'),
            created_by=self.user,
        )
        stock = SubproductStock.objects.create(subproduct=subp, quantity=Decimal('105.00'), created_by=self.user)
        self.assertTrue(subp.status)
        self.assertEqual(stock.quantity, Decimal('105.00'))

    def test_create_subproduct_with_initial_stock_zero_sets_status_false(self):
        subp = Subproduct.objects.create(
            parent=self.product,
            brand='TestBrand',
            number_coil=124,
            initial_stock_quantity=Decimal('0.00'),
            created_by=self.user,
        )
        stock = SubproductStock.objects.create(subproduct=subp, quantity=Decimal('0.00'), created_by=self.user)
        self.assertFalse(subp.status)
        self.assertEqual(stock.quantity, Decimal('0.00'))

    def test_stock_event_applies_status_change(self):
        subp = Subproduct.objects.create(
            parent=self.product,
            brand='TestBrand',
            number_coil=125,
            initial_stock_quantity=Decimal('0.00'),
            created_by=self.user,
        )
        stock = SubproductStock.objects.create(subproduct=subp, quantity=Decimal('0.00'), created_by=self.user)
        self.assertFalse(subp.status)
        # Aplica evento de ingreso
        event = StockEvent.objects.create(
            subproduct_stock=stock,
            quantity_change=Decimal('10.00'),
            event_type='ingreso_inicial',
            created_by=self.user,
        )
        stock.refresh_from_db()
        subp.refresh_from_db()
        self.assertEqual(stock.quantity, Decimal('10.00'))
        self.assertTrue(subp.status)
        # Aplica evento de egreso
        event2 = StockEvent.objects.create(
            subproduct_stock=stock,
            quantity_change=Decimal('-10.00'),
            event_type='egreso',
            created_by=self.user,
        )
        stock.refresh_from_db()
        subp.refresh_from_db()
        self.assertEqual(stock.quantity, Decimal('0.00'))
        self.assertFalse(subp.status)
