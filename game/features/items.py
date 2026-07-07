"""アイテム機能(担当:吉荒倖汰 
"""
from __future__ import annotations

import math

from typing import Any

from game.core import Feature, FPSGame, GameObject
class Items(Feature):
    """マップのHに回復パック、Aに弾薬パックを置き、触れたら拾えるようにする。"""

    name = "アイテム"

    def setup(self, game: FPSGame) -> None:
        self.game = game
        self.health_packs: list[GameObject] = [
            game.spawn_pickup(x, z, color=(74, 220, 92), name="health")
            for x, z in game.find_cells("H")
        ]
        self.ammo_packs: list[GameObject] = [
            game.spawn_pickup(x, z, color=(85, 172, 255), name="ammo")
            for x, z in game.find_cells("A")
        ]
        # ゴールドアイテムを配置する処理
        self.gold_items: list[GameObject] = [
            game.spawn_pickup(x, z, color=(255, 215, 0), name="gold")
            for x, z in game.find_cells("G")
        ]
        # レアアイテムを配置する処理
        self.rare_items: list[GameObject] = [
            game.spawn_pickup(x, z, color=(255, 0, 255), name="rare")
            for x, z in game.find_cells("R")
        ]

    def update(self, game: FPSGame, dt: float) -> None:
        # 追記: 全てのアイテム（回復パックと弾薬パック）をふわふわ回転させる
        for pack in self.health_packs + self.ammo_packs + self.gold_items + self.rare_items:
            pack.yaw += dt * 2.0
            pack.y = 0.3 + math.sin(game.time * 3.0) * 0.08

        for pack in self.health_packs[:]:
            if game.near_player(pack, 0.7) and game.player.health < game.player.max_health:
                game.heal_player(25)
                self._take(pack, self.health_packs)

        for pack in self.ammo_packs[:]:
            if game.near_player(pack, 0.7) and game.player.ammo < game.player.max_ammo:
                game.player.ammo = min(game.player.max_ammo, game.player.ammo + 15)
                game.flash((70, 170, 255), 0.25)
                self._take(pack, self.ammo_packs)
        
        # ゴールドアイテムを取ったときの処理
        for pack in self.gold_items[:]:
            if game.near_player(pack, 0.7):
                game.score += 100
                self._take(pack, self.gold_items)

        # レアアイテムを取ったときの処理
        for pack in self.rare_items[:]:
            if game.near_player(pack, 0.7):
                game.score += 500
                self._take(pack, self.rare_items)

    def _take(self, pack: GameObject, group: list[GameObject]) -> None:
        # パーティクルの色変更と数の増加
        self.game.spawn_particles(
            pack.x,
            pack.y,
            pack.z,
            color=(255, 220, 80),
            count=20
        )
        # フラッシュ演出を重ねる
        self.game.flash((255, 240, 120), 0.15)
        
        # 音担当に知らせる
        self.game.emit("item_picked", {
            "kind": pack.name
        })
        
        pack.remove()
        group.remove(pack)
