from django.forms import ModelForm
from pandas import NamedAgg
from .models import Room

class RoomForm(ModelForm):
  class Meta:
    model = Room
    fields = '__all__'
    # models.py から Room を持ってきて forms.py で新しくRoomFormを定義する。その中にfieldsでRoomの中の全部取得してるんじゃないすか？その後viewとかroom_form.htmlの方でなんかします

    # class Meta はわからないんだよなぁ

