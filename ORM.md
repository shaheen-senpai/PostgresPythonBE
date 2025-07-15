# Database Management Guide

This guide covers how to work with the database in the Postgress BE framework, including SQLAlchemy ORM usage and Alembic migration commands.

## Table of Contents

- [SQLAlchemy ORM Basics](#sqlalchemy-orm-basics)
- [Working with Models](#working-with-models)
- [Database Operations](#database-operations)
- [Alembic Migration Commands](#alembic-migration-commands)
- [Common Database Tasks](#common-database-tasks)
- [Best Practices](#best-practices)

## SQLAlchemy ORM Basics

SQLAlchemy ORM (Object Relational Mapper) allows you to interact with your database using Python objects instead of writing raw SQL.

### Key Components

- **Engine**: Connection to the database
- **Session**: Workspace for your database operations
- **Model**: Python class that maps to a database table
- **Relationship**: Connections between models

### How It Works in Our Framework

```python
# Database connection is configured in app/config/database.py
from app.config.database import get_db
from sqlalchemy.orm import Session

# Use the database session in your endpoints
@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

## Working with Models

### Creating a New Model

Create a new file in `app/models/` directory:

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Product(BaseModel):
    """Product model."""

    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    price = Column(Integer, nullable=False)

    # Define relationships
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
```

### Model Relationships

SQLAlchemy supports various relationship types:

1. **One-to-Many**:

   ```python
   # In Category model
   products = relationship("Product", back_populates="category")

   # In Product model
   category_id = Column(Integer, ForeignKey("categories.id"))
   category = relationship("Category", back_populates="products")
   ```

2. **Many-to-Many**:

   ```python
   # Association table
   product_tag = Table(
       "product_tags",
       BaseModel.metadata,
       Column("product_id", Integer, ForeignKey("products.id")),
       Column("tag_id", Integer, ForeignKey("tags.id"))
   )

   # In Product model
   tags = relationship("Tag", secondary=product_tag, back_populates="products")

   # In Tag model
   products = relationship("Product", secondary=product_tag, back_populates="tags")
   ```

3. **One-to-One**:

   ```python
   # In User model
   profile = relationship("Profile", uselist=False, back_populates="user")

   # In Profile model
   user_id = Column(Integer, ForeignKey("users.id"), unique=True)
   user = relationship("User", back_populates="profile")
   ```

## Database Operations

### Basic CRUD Operations

Our framework provides a `BaseController` class that implements common CRUD operations:

```python
from app.controllers.base_controller import BaseController
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class ProductController(BaseController[Product, ProductCreate, ProductUpdate]):
    """Controller for product operations."""

    def __init__(self):
        """Initialize with Product model."""
        super().__init__(Product)

    # Add custom methods here
    def get_by_category(self, db: Session, category_id: int):
        """Get products by category."""
        return db.query(self.model).filter(self.model.category_id == category_id).all()

# Create singleton instance
product_controller = ProductController()
```

### Common Query Operations

```python
# Get all records
products = db.query(Product).all()

# Get by ID
product = db.query(Product).filter(Product.id == product_id).first()

# Filter records
products = db.query(Product).filter(Product.price > 100).all()

# Order records
products = db.query(Product).order_by(Product.price.desc()).all()

# Limit and offset (pagination)
products = db.query(Product).offset(skip).limit(limit).all()

# Join queries
products = db.query(Product).join(Category).filter(Category.name == "Electronics").all()

# Count records
count = db.query(Product).filter(Product.price > 100).count()
```

### Transactions

```python
# Start a transaction
try:
    # Perform multiple operations
    db_obj = Product(name="New Product", price=100)
    db.add(db_obj)

    # Update another record
    other_obj = db.query(Product).filter(Product.id == 1).first()
    other_obj.price = 200
    db.add(other_obj)

    # Commit the transaction
    db.commit()
except Exception as e:
    # Rollback on error
    db.rollback()
    raise e
```

## Alembic Migration Commands

Alembic is a database migration tool for SQLAlchemy that helps you manage database schema changes over time.

### Creating Migrations

```bash
# Generate a new migration automatically by detecting model changes
alembic revision --autogenerate -m "Description of changes"

# Create an empty migration manually
alembic revision -m "Description of changes"
```

### Running Migrations

```bash
# Apply all migrations that haven't been applied yet
alembic upgrade head

# Apply migrations up to a specific version
alembic upgrade <revision_id>

# Apply next migration only
alembic upgrade +1

# Rollback last migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Rollback to a specific version
alembic downgrade <revision_id>
```

### Migration Information

```bash
# Show current migration version
alembic current

# Show migration history
alembic history

# Show detailed history with descriptions
alembic history -v

# Show pending migrations that haven't been applied
alembic history --indicate-current
```

### Other Useful Commands

```bash
# Show SQL that would be executed for a migration without running it
alembic upgrade <revision_id> --sql

# Stamp the database with a specific revision without running migrations
alembic stamp <revision_id>

# Check if the database is up to date
alembic check
```

## Common Database Tasks

### Adding a New Column to an Existing Table

1. Update your model:

   ```python
   # Add to your model
   new_column = Column(String(100), nullable=True)
   ```

2. Generate and run migration:
   ```bash
   alembic revision --autogenerate -m "Add new_column to table"
   alembic upgrade head
   ```

### Renaming a Column

Alembic doesn't detect column renames automatically. You need to create a manual migration:

```python
# In the migration file
def upgrade():
    op.alter_column('table_name', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('table_name', 'new_name', new_column_name='old_name')
```

### Creating Indexes

```python
# In your model
name = Column(String(100), nullable=False, index=True)

# Or create a composite index
__table_args__ = (
    Index('idx_name_price', 'name', 'price'),
)
```

### Data Migrations

For migrations that need to modify data:

```python
# In the migration file
def upgrade():
    # Create a table or add a column first if needed
    op.add_column('users', sa.Column('full_name', sa.String(100), nullable=True))

    # Get a reference to the table
    users = sa.table('users',
        sa.column('id', sa.Integer),
        sa.column('first_name', sa.String),
        sa.column('last_name', sa.String),
        sa.column('full_name', sa.String)
    )

    # Update data
    connection = op.get_bind()
    connection.execute(
        users.update().values(
            full_name=users.c.first_name + ' ' + users.c.last_name
        )
    )
```

## Best Practices

### Database Design

1. **Use appropriate column types**: Choose the right data type for each column
2. **Add constraints**: Use NOT NULL, UNIQUE, and foreign key constraints
3. **Create indexes**: Add indexes to columns used in WHERE clauses and joins
4. **Use relationships**: Define relationships between tables

### Migration Management

1. **Review auto-generated migrations**: Always check what Alembic generates
2. **Keep migrations small**: Make focused changes in each migration
3. **Test migrations**: Verify migrations work correctly before deploying
4. **Version control migrations**: Include migration files in your git repository

### Query Optimization

1. **Use specific queries**: Select only the columns you need
2. **Eager loading**: Use `joinedload()` or `selectinload()` to avoid N+1 query problems
3. **Pagination**: Always paginate large result sets
4. **Use indexes**: Ensure queries use indexed columns

### Security

1. **Parameterized queries**: Always use ORM parameters to prevent SQL injection
2. **Validate input**: Validate and sanitize all user input
3. **Limit access**: Use proper authentication and authorization

### Connection Management

1. **Use connection pooling**: Our framework configures this automatically
2. **Close sessions**: Always close database sessions when done
3. **Use transactions**: Wrap related operations in transactions
