import MODULE.SystemModule as SM
import MODULE.MapModule as MM
import MODULE.CharacterModule as CM
from COMMAND import Category100
import MODULE.InformModule as IM

SYSTEM = SM.System()

class Game:
    def __init__(self):
        global SYSTEM
        self.current = 0
        self.commands = None
        SYSTEM.GFLAG[0] = 3
        SYSTEM.delText(4)
        SYSTEM.after(self.phase0)
    
    def select_target(self, target:CM.Character):
        global SYSTEM
        MASTER = SYSTEM.CHARACTERS[SYSTEM.MASTER]
        CHARA:CM.Character = SYSTEM.CHARACTERS[self.current]
        CHARA.TARGET = target

        if CHARA in MASTER.CFLAG[11].SPACE:
            if target.TARGET == None:
                msg = f"{CHARA.NAME("은는")} {target.NAME()}에게 가까이 다가간다...\n"
            elif target.TARGET == CHARA:
                msg = f"{CHARA.NAME("은는")} 자신에게 다가온 {target.NAME()}에게 시선을 돌렸다.\n"
            else:
                msg = f"{CHARA.NAME("은는")} {target.TARGET.NAME("와과")} {target.NAME()} 사이에 끼어들었다!\n"

            SYSTEM.setText(4, msg)
    
    def current_info(self):
        global SYSTEM
        chara:CM.Character = SYSTEM.CHARACTERS[self.current]
        target_list = [target for target in chara.CFLAG[11].SPACE if target != chara]
        target_text = ' | '.join(target.NAME() for target in target_list)
        SYSTEM.setText(0, f"{SYSTEM.timeInfo} / 현재위치 : {chara.CFLAG[11].NAME} < {target_text} > ")
        current_text = SYSTEM.DISPLAY.textArea[0].get("1.0", "end-1c")
        start_index = 0
        for i, char in enumerate(target_list):
            if char == chara:
                continue
            start_index = current_text.find(char.NAME(), start_index)
            end_index = start_index + len(char.NAME())
            tagName = f"CHAR_{i}"
            SYSTEM.DISPLAY.textArea[0].tag_add(tagName, f"1.{start_index}", f"1.{end_index}")
            SYSTEM.DISPLAY.textArea[0].tag_bind(tagName, "<Enter>", lambda e, tag=tagName: SM.on_enter(e, tag))
            SYSTEM.DISPLAY.textArea[0].tag_bind(tagName, "<Leave>", lambda e, tag=tagName: SM.on_leave(e, tag))
            SYSTEM.DISPLAY.textArea[0].tag_bind(tagName, "<Button-1>", lambda e, target = char : self.select_target(target))
            start_index = end_index + 3  # +3 for the ' | '
    
    # 기본설정
    def phase0(self):
        global SYSTEM
        MASTER = SYSTEM.CHARACTERS[SYSTEM.MASTER]
        CHARA:CM.Character = SYSTEM.CHARACTERS[self.current]

        SYSTEM.RESULT = 0

        # 대상의 존재여부 확인 / 같은 방에 있어야만 선택된 상태로 유지됨
        if CHARA.TARGET != None:
            if CHARA.TARGET not in CHARA.CFLAG[11].SPACE:
                CHARA.TARGET = None
        
        # 대상이 없을 경우 대상을 선택함 / 현재는 33.3% 확률로 선정함
        if CHARA != MASTER and CHARA.TARGET == None and len(CHARA.CFLAG[11].SPACE) > 1:
            RESULT = SYSTEM.RANDOM(3)
            targets = [chara for chara in CHARA.CFLAG[11].SPACE if chara != CHARA]
            if RESULT == 1:
                self.select_target(SYSTEM.CHOICE(targets))

        # 플레이어 턴인지 여부를 확인함
        if self.current == SYSTEM.MASTER:
            SYSTEM.after(self.phase1)
        else:
            SYSTEM.after(self.phase2)

    # 화면에 출력할 정보 준비
    def phase1(self):
        global SYSTEM

        # 최신정보 출력을 위해 기존 내역을 전부 제거함
        SYSTEM.delText(0)
        SYSTEM.delText(1)
        SYSTEM.delText(2)
        SYSTEM.delText(3)

        chara:CM.Character = SYSTEM.CHARACTERS[self.current]

        # 0번 텍스트 위젯 : 시간 및 선택가능한 캐릭터 출력
        self.current_info()

            # 1번 텍스트 위젯 - 아나타의 파라미터 출력
        IM.showParam(1, chara)

            # 2번 텍스트 위젯 - 선택된 캐릭터가 있을 경우 선택된 캐릭터의 파라미터 출력
        if chara.TARGET != None:
            IM.showParam(2, chara.TARGET)
            
        # 3번 텍스트 위젯 - 지도 출력
        MM.showMap(chara.CFLAG[11].ID)

        SYSTEM.after(self.phase2)
        
    # 메뉴를 출력하고 입력을 받음 - 사용자 턴일 경우
    def phase2(self):
        global SYSTEM
        if self.current == SYSTEM.MASTER:
            SYSTEM.input(SYSTEM.COM, 20, 5, "left")
        else:
            SYSTEM.inputr(SYSTEM.COM)
        
        SYSTEM.after(self.phase3)
    
    # 선택된 메뉴에 따라 행동을 실행함
    def phase3(self):
        global SYSTEM
        
        RESULT = SYSTEM.RESULT

        if RESULT == 0:
            return
        elif RESULT == 1000:
            SYSTEM.after(self.phase0)
        elif RESULT == 1002:
            SYSTEM.after(self.phase2)
        else:
            chara:CM.Character = SYSTEM.CHARACTERS[self.current]
            SYSTEM.COM[RESULT][1](chara)
            self.current += 1
            if self.current == (len(SYSTEM.CHARACTERS) - 1):
                self.current = 0
            SYSTEM.after(SYSTEM.see_end)
            SYSTEM.after(self.phase0)

def simulation():
    game = Game()
