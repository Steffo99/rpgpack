from typing import *
import royalnet
import royalnet.commands as rc
import royalnet.utils as ru
from ..types import Faction
from ..tables import DndBattleUnit
from ..utils import get_active_battle


class DndaddunitCommand(rc.Command):
    name: str = "dndaddunit"

    description: str = "Add an Unit to a Battle."

    aliases = ["dau", "dndau", "addunit", "daddunit"]

    syntax: str = "{faction} {name} {initiative} {health} {armorclass}"

    async def run(self, args: rc.CommandArgs, data: rc.CommandData) -> None:
        faction = Faction[args[0].upper()]
        name = args[1]
        initiative = int(args[2])
        health = args[3]
        armor_class = int(args[4])

        DndBattleUnitT = self.alchemy.get(DndBattleUnit)

        active_battle = await get_active_battle(data)
        if active_battle is None:
            raise rc.CommandError("No battle is active in this chat.")

        units_with_same_name = await ru.asyncify(data.session.query(DndBattleUnitT).filter_by(
            name=name,
            battle=active_battle.battle
        ).all)

        if len(units_with_same_name) != 0:
            raise rc.InvalidInputError("A unit with the same name already exists.")

        dbu = DndBattleUnitT(
            linked_character_id=None,
            initiative=initiative,
            faction=faction,
            name=name,
            health_string=health,
            armor_class=armor_class,
            battle=active_battle.battle
        )

        data.session.add(dbu)
        await data.session_commit()

        await data.reply(f"{dbu}\n"
                         f"joins the battle!")

        if dbu.health.hidden:
            await data.delete_invoking()