from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import Snippet, SnippetRequest, SkriptVersion
import uuid

router = APIRouter(tags=["snippets"])

class SnippetsService:
    def __init__(self):
        self.snippets = [
            Snippet(
                id="snippet_001",
                title="Welcome Message System",
                description="Shows welcome message with configurable first-join rewards",
                code="""options:
    prefix: &6[Server]&r
    first-join-money: 1000

on join:
    if {joined::%player's uuid%} is not set:
        set {joined::%player's uuid%} to true
        set {money::%player's uuid%} to {@first-join-money}
        wait 1 second
        send "&a&lWELCOME TO THE SERVER!" to player
        send "&7This is your first time here!" to player
        send "&7You received &e${@first-join-money} &7as a welcome gift!" to player
        broadcast "{@prefix} &e%player% &7joined for the first time!"
    else:
        send "{@prefix} &7Welcome back, &e%player%&7!" to player""",
                category="player_events",
                tags=["join", "welcome", "first-join", "economy"],
                author="SkriptAPI",
                version_compatible=[SkriptVersion.V2_12_0, SkriptVersion.V2_11_2],
                requires_addons=[]
            ),
            Snippet(
                id="snippet_002",
                title="Anti-Grief Protection",
                description="Basic protection system with bypass permission",
                code="""on block break:
    if {protected::%chunk of event-block%} is set:
        if player doesn't have permission "protection.bypass":
            if {protected::%chunk of event-block%::owner} is not player's uuid:
                cancel event
                send "&c&lPROTECTED AREA" to player
                send "&7This area belongs to &e%{protected::%chunk of event-block%::name}%" to player

on block place:
    if {protected::%chunk of event-block%} is set:
        if player doesn't have permission "protection.bypass":
            if {protected::%chunk of event-block%::owner} is not player's uuid:
                cancel event
                send "&cYou cannot build in this protected area!" to player

command /protect:
    description: Protect the chunk you're standing in
    permission: protection.claim
    trigger:
        if {protected::%chunk of player%} is set:
            send "&cThis chunk is already protected!" to player
            stop
        set {protected::%chunk of player%} to true
        set {protected::%chunk of player%::owner} to player's uuid
        set {protected::%chunk of player%::name} to player's name
        send "&aChunk protected successfully!" to player""",
                category="protection",
                tags=["grief", "protection", "claim", "chunk"],
                author="SkriptAPI",
                version_compatible=[SkriptVersion.V2_12_0, SkriptVersion.V2_11_2],
                requires_addons=[]
            ),
            Snippet(
                id="snippet_003",
                title="Custom Death Messages",
                description="Customizable death messages based on cause",
                code="""on death:
    if victim is a player:
        set death message to ""
        
        if attacker is a player:
            broadcast "&c%victim% &7was slain by &c%attacker%"
            add 1 to {kills::%attacker's uuid%}
            add 1 to {deaths::%victim's uuid%}
        else if attacker is set:
            broadcast "&c%victim% &7was killed by a %type of attacker%"
            add 1 to {deaths::%victim's uuid%}
        else:
            if damage cause is fall:
                broadcast "&c%victim% &7fell from a high place"
            else if damage cause is drowning:
                broadcast "&c%victim% &7drowned"
            else if damage cause is fire or damage cause is lava:
                broadcast "&c%victim% &7burned to death"
            else:
                broadcast "&c%victim% &7died"
            add 1 to {deaths::%victim's uuid%}
        
        send "&7You died! Use &e/back &7to return to your death location" to victim
        set {back::%victim's uuid%} to victim's location""",
                category="combat",
                tags=["death", "pvp", "messages", "kills"],
                author="SkriptAPI",
                version_compatible=[SkriptVersion.V2_12_0, SkriptVersion.V2_11_2],
                requires_addons=[]
            ),
            Snippet(
                id="snippet_004",
                title="Voting Rewards System",
                description="Give rewards when players vote for the server",
                code="""command /vote:
    description: Get voting links and check status
    trigger:
        send "&6&lVOTING LINKS:" to player
        send "&e1. &7vote.server1.com" to player
        send "&e2. &7vote.server2.com" to player
        send "&e3. &7vote.server3.com" to player
        send "" to player
        send "&7Vote on all sites to get rewards!" to player
        send "&7Votes today: &e%{votes::%player's uuid%::today} ? 0%" to player

command /fakevote [<offline player>]:
    description: Simulate a vote (admin only)
    permission: vote.admin
    trigger:
        set {_player} to arg-1 ? player
        execute console command "vote %{_player}%"

command /vote <offline player>:
    description: Process vote reward
    permission: vote.process
    executable by: console
    trigger:
        add 1 to {votes::%arg-1's uuid%::total}
        add 1 to {votes::%arg-1's uuid%::today}
        
        if arg-1 is online:
            send "&a&lThank you for voting!" to arg-1
            give 1 diamond to arg-1
            add 100 to {money::%arg-1's uuid%}
            send "&7Rewards: &b1 Diamond &7and &e$100" to arg-1
            
            if {votes::%arg-1's uuid%::today} >= 3:
                give 1 emerald to arg-1
                send "&6&lBONUS! &7You voted on all sites today! Extra: &a1 Emerald" to arg-1
        else:
            set {vote.reward::%arg-1's uuid%} to true
            
        broadcast "&e%arg-1% &7voted for the server! &e/vote"

on join:
    if {vote.reward::%player's uuid%} is true:
        delete {vote.reward::%player's uuid%}
        send "&a&lYou have pending vote rewards!" to player
        give 1 diamond to player
        add 100 to {money::%player's uuid%}
        send "&7Rewards: &b1 Diamond &7and &e$100" to player""",
                category="rewards",
                tags=["vote", "rewards", "economy"],
                author="SkriptAPI",
                version_compatible=[SkriptVersion.V2_12_0, SkriptVersion.V2_11_2],
                requires_addons=[]
            ),
            Snippet(
                id="snippet_005",
                title="AFK Detection System",
                description="Detect and manage AFK players",
                code="""every 1 second:
    loop all players:
        if {afk.location::%loop-player's uuid%} is loop-player's location:
            add 1 to {afk.time::%loop-player's uuid%}
            
            if {afk.time::%loop-player's uuid%} >= 300:  # 5 minutes
                if {afk::%loop-player's uuid%} is not true:
                    set {afk::%loop-player's uuid%} to true
                    set loop-player's display name to "&7[AFK] %loop-player%"
                    broadcast "&7%loop-player% is now AFK"
        else:
            set {afk.location::%loop-player's uuid%} to loop-player's location
            if {afk::%loop-player's uuid%} is true:
                delete {afk::%loop-player's uuid%}
                set loop-player's display name to loop-player's name
                broadcast "&7%loop-player% is no longer AFK"
            delete {afk.time::%loop-player's uuid%}

on quit:
    delete {afk::%player's uuid%}
    delete {afk.time::%player's uuid%}
    delete {afk.location::%player's uuid%}

command /afk:
    description: Toggle AFK status
    trigger:
        if {afk::%player's uuid%} is not true:
            set {afk::%player's uuid%} to true
            set {afk.time::%player's uuid%} to 300
            set player's display name to "&7[AFK] %player%"
            broadcast "&7%player% is now AFK"
        else:
            delete {afk::%player's uuid%}
            delete {afk.time::%player's uuid%}
            set player's display name to player's name
            broadcast "&7%player% is no longer AFK" """,
                category="utility",
                tags=["afk", "idle", "detection"],
                author="SkriptAPI",
                version_compatible=[SkriptVersion.V2_12_0, SkriptVersion.V2_11_2],
                requires_addons=[]
            ),
            Snippet(
                id="snippet_006",
                title="Random Teleport System",
                description="Teleport players to random safe locations",
                code="""command /rtp:
    description: Teleport to a random location
    cooldown: 30 seconds
    cooldown message: &cYou must wait %remaining time% before using RTP again!
    trigger:
        send "&7Finding a safe location..." to player
        set {_tries} to 0
        while {_tries} < 50:
            add 1 to {_tries}
            set {_x} to random integer between -5000 and 5000
            set {_z} to random integer between -5000 and 5000
            set {_loc} to location at {_x}, 255, {_z} in player's world
            
            loop blocks from {_loc} to location at {_x}, 50, {_z} in player's world:
                if loop-block is not air:
                    set {_y} to y-coordinate of loop-block + 1
                    set {_loc} to location at {_x}, {_y}, {_z} in player's world
                    
                    if block at {_loc} is air:
                        if block at location 1 above {_loc} is air:
                            if block at location 1 below {_loc} is not air:
                                if block at location 1 below {_loc} is not lava:
                                    if block at location 1 below {_loc} is not water:
                                        teleport player to {_loc}
                                        send "&aYou've been teleported to a random location!" to player
                                        send "&7Coordinates: &eX: %{_x}% Y: %{_y}% Z: %{_z}%" to player
                                        stop
        
        send "&cCouldn't find a safe location! Try again." to player""",
                category="teleportation",
                tags=["rtp", "random", "teleport", "wild"],
                author="SkriptAPI",
                version_compatible=[SkriptVersion.V2_12_0, SkriptVersion.V2_11_2],
                requires_addons=[]
            ),
            Snippet(
                id="snippet_007",
                title="Chat Formatting & Ranks",
                description="Custom chat format with rank prefixes",
                code="""on chat:
    cancel event
    
    if {muted::%player's uuid%} is true:
        send "&cYou are muted!" to player
        stop
    
    set {_prefix} to ""
    set {_suffix} to ""
    
    if player has permission "rank.owner":
        set {_prefix} to "&4[OWNER]&r"
    else if player has permission "rank.admin":
        set {_prefix} to "&c[ADMIN]&r"
    else if player has permission "rank.mod":
        set {_prefix} to "&2[MOD]&r"
    else if player has permission "rank.vip":
        set {_prefix} to "&6[VIP]&r"
    else:
        set {_prefix} to "&7[MEMBER]&r"
    
    if {level::%player's uuid%} is set:
        set {_suffix} to "&7[Lvl %{level::%player's uuid%}%]"
    
    set {_format} to "%{_prefix}% %player's display name%%{_suffix}%&7: &f%message%"
    
    loop all players:
        if distance between player and loop-player <= 100:
            send {_format} to loop-player
        else if player has permission "chat.global":
            if message starts with "!":
                send "&7[GLOBAL] %{_format}%" to loop-player

command /mute <offline player> [<timespan>]:
    description: Mute a player
    permission: chat.mute
    trigger:
        if arg-2 is set:
            set {muted::%arg-1's uuid%} to true
            set {mute.expire::%arg-1's uuid%} to now + arg-2
            send "&cYou muted %arg-1% for %arg-2%!" to player
            if arg-1 is online:
                send "&cYou have been muted for %arg-2%!" to arg-1
        else:
            set {muted::%arg-1's uuid%} to true
            send "&cYou muted %arg-1% permanently!" to player
            if arg-1 is online:
                send "&cYou have been muted!" to arg-1""",
                category="chat",
                tags=["chat", "format", "ranks", "mute"],
                author="SkriptAPI",
                version_compatible=[SkriptVersion.V2_12_0, SkriptVersion.V2_11_2],
                requires_addons=[]
            )
        ]
    
    def search_snippets(self, search: Optional[str] = None, 
                       category: Optional[str] = None, 
                       tags: Optional[List[str]] = None) -> List[Snippet]:
        results = self.snippets
        
        if search:
            search_lower = search.lower()
            results = [s for s in results if (
                search_lower in s.title.lower() or
                search_lower in s.description.lower() or
                search_lower in s.code.lower() or
                any(search_lower in tag for tag in s.tags)
            )]
        
        if category:
            results = [s for s in results if s.category == category]
            
        if tags:
            results = [s for s in results if any(tag in s.tags for tag in tags)]
            
        return results
    
    def get_snippet_by_id(self, snippet_id: str) -> Optional[Snippet]:
        for snippet in self.snippets:
            if snippet.id == snippet_id:
                return snippet
        return None
    
    def get_categories(self) -> List[str]:
        return list(set(s.category for s in self.snippets))
    
    def get_all_tags(self) -> List[str]:
        tags = set()
        for snippet in self.snippets:
            tags.update(snippet.tags)
        return sorted(list(tags))

snippets_service = SnippetsService()

@router.post("/snippets/search")
async def search_snippets(request: SnippetRequest):
    try:
        results = snippets_service.search_snippets(
            request.search,
            request.category,
            request.tags
        )
        return {
            "snippets": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/snippets")
async def get_all_snippets():
    return {
        "snippets": snippets_service.snippets,
        "total": len(snippets_service.snippets)
    }

@router.get("/snippets/categories")
async def get_snippet_categories():
    return {
        "categories": snippets_service.get_categories()
    }

@router.get("/snippets/tags")
async def get_all_tags():
    return {
        "tags": snippets_service.get_all_tags()
    }

@router.get("/snippets/{snippet_id}")
async def get_snippet(snippet_id: str):
    snippet = snippets_service.get_snippet_by_id(snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return snippet