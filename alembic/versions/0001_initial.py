from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('token_blocklist',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('jti', sa.String(length=36), nullable=False, unique=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=80), nullable=False, unique=True),
        sa.Column('email', sa.String(length=120), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table('documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=128)),
        sa.Column('text', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table('concepts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, index=True),
        sa.Column('category', sa.String(length=64)),
        sa.Column('importance', sa.Float()),
        sa.Column('difficulty', sa.String(length=32)),
        sa.Column('description', sa.Text()),
    )

    op.create_table('exercises',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('concept_id', sa.Integer(), sa.ForeignKey('concepts.id'), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('question', sa.Text()),
        sa.Column('answer', sa.Text()),
        sa.Column('estimated_time', sa.Integer()),
        sa.Column('difficulty', sa.String(length=32)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('exercises')
    op.drop_table('concepts')
    op.drop_table('documents')
    op.drop_table('users')
    op.drop_table('token_blocklist')
