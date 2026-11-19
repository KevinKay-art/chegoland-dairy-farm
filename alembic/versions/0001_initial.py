"""initial migration

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False, server_default='customer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'])

    op.create_table(
        'cows',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tag_number', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('breed', sa.String(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('photo_url', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='lactating'),
        sa.Column('daily_avg_yield', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cows_tag_number'), 'cows', ['tag_number'], unique=True)
    op.create_index(op.f('ix_cows_breed'), 'cows', ['breed'])
    op.create_index(op.f('ix_cows_status'), 'cows', ['status'])

    op.create_table(
        'products',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_slug'), 'products', ['slug'], unique=True)
    op.create_index(op.f('ix_products_category'), 'products', ['category'])
    op.create_index(op.f('ix_products_is_active'), 'products', ['is_active'])
    op.create_index(op.f('ix_products_is_featured'), 'products', ['is_featured'])

    op.create_table(
        'orders',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('order_number', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('customer_name', sa.String(), nullable=False),
        sa.Column('customer_phone', sa.String(), nullable=False),
        sa.Column('customer_email', sa.String(), nullable=True),
        sa.Column('delivery_address', sa.String(), nullable=False),
        sa.Column('delivery_date', sa.String(), nullable=True),
        sa.Column('delivery_time_slot', sa.String(), nullable=True),
        sa.Column('payment_method', sa.String(), nullable=False),
        sa.Column('payment_status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('order_status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('subtotal', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('delivery_fee', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_order_number'), 'orders', ['order_number'], unique=True)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'])
    op.create_index(op.f('ix_orders_order_status'), 'orders', ['order_status'])
    op.create_index(op.f('ix_orders_payment_status'), 'orders', ['payment_status'])

    op.create_table(
        'order_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('order_id', sa.String(), nullable=False),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'])
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'])

    op.create_table(
        'milk_records',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('cow_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('session', sa.String(), nullable=False),
        sa.Column('yield_litres', sa.Float(), nullable=False),
        sa.Column('used_by_calves', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('spoiled', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('available_for_sale', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['cow_id'], ['cows.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_milk_records_cow_id'), 'milk_records', ['cow_id'])
    op.create_index(op.f('ix_milk_records_date'), 'milk_records', ['date'])
    op.create_index(op.f('ix_milk_records_cow_date'), 'milk_records', ['cow_id', 'date'])

    op.create_table(
        'payments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('order_id', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('payment_method', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('transaction_id', sa.String(), nullable=True),
        sa.Column('mpesa_receipt_number', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('checkout_request_id', sa.String(), nullable=True),
        sa.Column('merchant_request_id', sa.String(), nullable=True),
        sa.Column('response_code', sa.String(), nullable=True),
        sa.Column('response_description', sa.String(), nullable=True),
        sa.Column('raw_callback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'])
    op.create_index(op.f('ix_payments_transaction_id'), 'payments', ['transaction_id'])
    op.create_index(op.f('ix_payments_checkout_request_id'), 'payments', ['checkout_request_id'])
    op.create_index(op.f('ix_payments_status'), 'payments', ['status'])

    op.create_table(
        'health_records',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('cow_id', sa.String(), nullable=False),
        sa.Column('record_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('next_due_date', sa.Date(), nullable=True),
        sa.Column('cost', sa.String(), nullable=True),
        sa.Column('vet_name', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['cow_id'], ['cows.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_records_cow_id'), 'health_records', ['cow_id'])
    op.create_index(op.f('ix_health_records_date'), 'health_records', ['date'])

    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('frequency', sa.String(), nullable=False, server_default='daily'),
        sa.Column('start_date', sa.String(), nullable=False),
        sa.Column('end_date', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('next_delivery_date', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'])
    op.create_index(op.f('ix_subscriptions_product_id'), 'subscriptions', ['product_id'])
    op.create_index(op.f('ix_subscriptions_is_active'), 'subscriptions', ['is_active'])

    op.create_table(
        'contact_messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('contact_messages')
    op.drop_table('subscriptions')
    op.drop_table('health_records')
    op.drop_table('payments')
    op.drop_table('milk_records')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('cows')
    op.drop_table('users')