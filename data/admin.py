import os
from datetime import datetime

from jose import jwt
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from data.models import Category, Tag, OptionItem, OptionType, ItemType, User, Ad, Order


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        # We expect users to be already authenticated through the frontend
        return await self.authenticate(request)

    async def logout(self, request: Request) -> bool:
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.cookies.get('token')

        if not token:
            return False

        result = jwt.decode(token, key=os.environ['JWT_SECRET_KEY'], algorithms=['HS256'])
        result['exp'] = datetime.fromtimestamp(result['exp'])
        if datetime.now() > result['exp']:
            return False
        if 'admin.cms' not in result['permissions']:
            return False
        return True


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.name]
    column_searchable_list = [Category.name]
    name_plural = 'Categories'
    column_labels = {
        Category.name: 'Name'
    }


class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.name, Tag.color]
    column_searchable_list = [Tag.name]
    column_labels = {
        Tag.name: 'Name',
        Tag.color: 'Color (#ffffff)'
    }


class OptionItemAdmin(ModelView, model=OptionItem):
    column_list = [OptionItem.name, OptionItem.priceChange, OptionItem.type, OptionItem.isDefault]
    column_searchable_list = [OptionItem.name]
    column_labels = {
        OptionItem.name: 'Name',
        OptionItem.priceChange: 'Price Change',
        OptionItem.type: 'Type',
        OptionItem.isDefault: 'Select By Default'
    }


class OptionTypeAdmin(ModelView, model=OptionType):
    column_list = [OptionType.name]
    column_searchable_list = [OptionType.name]
    column_labels = {
        OptionType.name: 'Name'
    }


class ItemTypeAdmin(ModelView, model=ItemType):
    column_list = [ItemType.category, ItemType.name, ItemType.image, ItemType.tags, ItemType.description, ItemType.shortDescription, ItemType.basePrice, ItemType.salePercent, ItemType.options]
    column_searchable_list = [ItemType.name]
    column_labels = {
        ItemType.category: 'Category',
        ItemType.name: 'Name',
        ItemType.image: 'Image',
        ItemType.tags: 'Tags',
        ItemType.description: 'Long Description',
        ItemType.shortDescription: 'Short Description',
        ItemType.basePrice: 'Base Price',
        ItemType.salePercent: 'Sale Percent (0 to 1)',
        ItemType.options: 'Applicable Option Types'
    }


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.pinyin, User.phone, User.permissions, User.blocked]
    column_searchable_list = [User.id, User.name, User.pinyin]
    column_labels = {
        User.id: 'ID',
        User.name: 'Name',
        User.pinyin: 'Name (Pinyin)',
        User.phone: 'Phone Number',
        User.permissions: 'Permissions',
        User.blocked: 'Blocked'
    }

    can_create = False


class AdAdmin(ModelView, model=Ad):
    column_list = [Ad.name, Ad.image, Ad.url]
    column_searchable_list = [Ad.name]
    column_labels = {
        Ad.name: 'Name (Not Shown)',
        Ad.image: 'Image',
        Ad.url: 'URL'
    }


class OrderAdmin(ModelView, model=Order):
    column_list = [Order.id, Order.items, Order.totalPrice, Order.number, Order.status, Order.createdTime, Order.type, Order.deliveryRoom, Order.user, Order.onSiteName]
    column_searchable_list = [Order.id]
    column_labels = {
        Order.id: 'ID',
        Order.items: 'Items Ordered',
        Order.totalPrice: 'Total Price',
        Order.number: 'Number',
        Order.status: 'Status',
        Order.createdTime: 'Created Time',
        Order.type: 'Type',
        Order.deliveryRoom: 'Delivery Room',
        Order.user: 'Ordered By',
        Order.onSiteName: 'Name (for on-site ordering)'
    }

    can_create = False
    can_delete = False
    can_edit = False
    can_export = False


def create_admin(app, engine):
    admin = Admin(app, engine,
                  authentication_backend=AdminAuth(secret_key='what-you-love-is-your-life'),
                  title='Whale CMS')
    admin.add_view(CategoryAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(OptionItemAdmin)
    admin.add_view(OptionTypeAdmin)
    admin.add_view(ItemTypeAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(AdAdmin)
    return admin
