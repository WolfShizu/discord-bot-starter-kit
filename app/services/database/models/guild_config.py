from sqlalchemy import BigInteger, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.database.engine import Base

class GuildConfig(Base):
    __tablename__ = "guild_configs"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key= True)
    prefix: Mapped[str] = mapped_column(default= "!")

    admin_roles: Mapped[list[int]] = mapped_column(JSON, default= list)
    allowed_roles: Mapped[list[int]] = mapped_column(JSON, default= list)
    denied_roles: Mapped[list[int]] = mapped_column(JSON, default= list)

    # Relação local. Não é aplicada ao banco de dados
    channels: Mapped[list["ChannelConfig"]] = relationship(back_populates= "guild", cascade= "all, delete-orphan")

class ChannelConfig(Base):
    __tablename__ = "channels_configs"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key= True)

    guild_id: Mapped[int] = mapped_column(ForeignKey("guild_configs.guild_id"))

    allowed_roles: Mapped[list[int]] = mapped_column(JSON, default= list)
    denied_roles: Mapped[list[int]] = mapped_column(JSON, default= list)
    allowed_users: Mapped[list[int]] = mapped_column(JSON, default= list)
    denied_users: Mapped[list[int]] = mapped_column(JSON, default= list)

    # Relação local. Não é aplicada ao banco de dados
    guild: Mapped["GuildConfig"] = relationship(back_populates= "channels")
