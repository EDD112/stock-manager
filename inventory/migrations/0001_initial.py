from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('color', models.CharField(
                    choices=[
                        ('#3b82f6', 'Blue'), ('#06b6d4', 'Cyan'), ('#ef4444', 'Red'),
                        ('#f59e0b', 'Yellow/Amber'), ('#8b5cf6', 'Purple'), ('#ec4899', 'Pink'),
                        ('#f97316', 'Orange'), ('#10b981', 'Green'), ('#6b7280', 'Gray'),
                        ('#dc2626', 'Dark Red'), ('#0d9488', 'Teal'), ('#7c3aed', 'Violet'),
                    ],
                    default='#6b7280', max_length=7,
                )),
                ('icon', models.CharField(
                    choices=[
                        ('fa-wine-bottle', 'Bottle (Beverage)'), ('fa-snowflake', 'Snowflake (Freezer)'),
                        ('fa-pepper-hot', 'Pepper (Condiment)'), ('fa-cheese', 'Cheese (Dairy)'),
                        ('fa-cookie', 'Cookie (Canned/Tin)'), ('fa-cookie-bite', 'Cookie Bite (Snack)'),
                        ('fa-bread-slice', 'Bread (Bakery)'), ('fa-drumstick-bite', 'Drumstick (Meat)'),
                        ('fa-fish', 'Fish (Seafood)'), ('fa-apple-alt', 'Apple (Produce)'),
                        ('fa-seedling', 'Seedling (Organic)'), ('fa-coffee', 'Coffee (Hot Drinks)'),
                        ('fa-ice-cream', 'Ice Cream (Frozen Desserts)'), ('fa-carrot', 'Carrot (Vegetables)'),
                        ('fa-box', 'Box (General/Other)'), ('fa-tags', 'Tag (Misc)'),
                    ],
                    default='fa-box', max_length=50,
                )),
            ],
            options={
                'verbose_name': 'Category Type',
                'verbose_name_plural': 'Category Types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('category_type', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='categories',
                    to='inventory.categorytype',
                )),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('quantity', models.IntegerField(default=0)),
                ('expiry_date', models.DateField()),
                ('status', models.CharField(
                    choices=[('In Stock', 'In Stock'), ('Low Stock', 'Low Stock'), ('Out of Stock', 'Out of Stock')],
                    default='In Stock', editable=False, max_length=50,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('deactivated_at', models.DateTimeField(blank=True, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='products',
                    to='inventory.category',
                )),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProductBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('expiry_date', models.DateField()),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='batches',
                    to='inventory.product',
                )),
                ('added_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Product Batch',
                'verbose_name_plural': 'Product Batches',
                'ordering': ['expiry_date', 'date_added'],
            },
        ),
    ]
