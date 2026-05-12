# Horse Lose Poses Requests

Source of truth: D:\Work\LAMDiceBot\docs\spritemake-request\2026-05-05-horse-lose-poses.md

## Source 참조 (스타일 매칭 -- 필수)

- Main SVG definition: D:\Work\LAMDiceBot\js\horse-race-sprites.js
- Use each base svgMap vehicle object's run.frame1 SVG markup as the style reference.
- Do not use POWER_VEHICLE_VARIANT_OVERRIDES, booster, or power-state art.
- Line anchors:
  - car: L3
  - rocket: L49
  - bird: L91
  - boat: L135
  - bicycle: L169
  - rabbit: L217
  - turtle: L275
  - eagle: L315
  - scooter: L363
  - helicopter: L405
  - horse: L463
  - knight: L886
  - dinosaur: L1267
  - ninja: L1677
  - crab: L2027
- Additional tone references only:
  - D:\Work\LAMDiceBot\assets\backgrounds\vehicle-flat\horse.png
  - D:\Work\LAMDiceBot\assets\backgrounds\vehicle-generated\horse.png
- Source SVG viewBox sizes may vary. Output lose atlases are normalized to 120x45 total, 2 horizontal 60x45 cells.

## Common Runtime Contract

- Canvas: 120x45 px
- Grid: 2 columns x 1 row
- Cell: 60x45 px
- Column boundaries: x=0, 60, 120
- Row boundaries: y=0, 45
- Contact anchor: x=30, y=45, track ground contact at bottom center
- Y-axis baseline/source plane: y=45, vehicle feet/bottom touches cell bottom in both frames
- Animation: 2 frames, 0.6s total loop, subtle sad breathing only
- Format: transparent PNG-32 RGBA, straight alpha, sRGB
- Required model: gpt-image-2 only

## Assets

### horse-lose (말)

- Asset role: 패배(당첨자) 자세 - 무릎 꿇은 말 + 고개 숙임
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/horse-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 463, vehicle 'horse' base svgMap run.frame1 state
- Additional PNG reference: D:\Work\LAMDiceBot\assets\backgrounds\vehicle-flat\horse.png
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/horse-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/horse-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 무릎 꿇음 + 고개 숙임; col 1 = 한숨 구름이 살짝 움직이고 몸이 1px 들썩임
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 갈색/베이지 말, 갈기 헝클어짐, 눈은 ㅠㅠ 모양
- QA priority: high

### rabbit-lose (토끼)

- Asset role: 패배 자세 - 토끼 귀가 처지고 주저앉은 자세
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/rabbit-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 217, vehicle 'rabbit' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/rabbit-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/rabbit-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 귀가 처진 채 주저앉음; col 1 = 한숨과 함께 몸이 1px 가라앉음
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 흰색/회색 토끼, 양쪽 귀가 머리 옆으로 축 처짐, 한쪽 발 펴고 앉아있는 자세
- QA priority: high

### turtle-lose (거북이)

- Asset role: 패배 자세 - 등껍질 안으로 머리와 발이 살짝 들어간 모습
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/turtle-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 275, vehicle 'turtle' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/turtle-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/turtle-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 등껍질 안으로 움츠림; col 1 = 구름이 살짝 위로 움직이고 머리가 1px 더 들어감
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 초록색 거북이, 머리와 다리가 등껍질 안으로 절반쯤 들어감, 등껍질 위에 작은 구름
- QA priority: high

### dinosaur-lose (공룡)

- Asset role: 패배 자세 - 꼬리 늘어뜨리고 고개 숙인 공룡
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/dinosaur-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 1267, vehicle 'dinosaur' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/dinosaur-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/dinosaur-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 꼬리 늘어뜨리고 고개 숙임; col 1 = 슬픈 호흡으로 머리와 구름이 1px 움직임
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 초록 공룡(티라노 풍), 짧은 앞발 살짝 들고, 꼬리 땅에 늘어짐, 머리 옆으로 살짝 숙임
- QA priority: high

### knight-lose (기사)

- Asset role: 패배 자세 - 검을 땅에 짚고 무릎 꿇은 기사
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/knight-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 886, vehicle 'knight' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/knight-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/knight-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 검을 땅에 짚고 한쪽 무릎 꿇음; col 1 = 투구가 1px 숙여지고 한숨 효과 이동
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 은색 갑옷 기사, 한쪽 무릎 꿇음, 검 끝을 땅에 짚음, 투구 안 눈은 ㅠㅠ 또는 가늘게
- QA priority: high

### car-lose (자동차)

- Asset role: 패배 자세 - 멈춰서 헤드라이트 꺼지고 운전자 한숨
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/car-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 3, vehicle 'car' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/car-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/car-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 멈춘 차체가 살짝 처짐; col 1 = 구름이 움직이고 차체가 1px 더 내려앉음
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 빨간색 컴팩트카, 정지 상태, 보닛 위에 작은 구름, 약간 처진 차체(서스펜션 압축)
- QA priority: medium

### rocket-lose (로켓)

- Asset role: 패배 자세 - 분사 멈추고 비스듬히 떨어지는 로켓
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/rocket-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 49, vehicle 'rocket' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/rocket-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/rocket-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 분사 없이 5도 기울어진 로켓; col 1 = 연기가 1px 이동하고 로켓이 살짝 가라앉음
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 빨간 로켓, 5도 옆으로 기울어짐, 분사구에서 회색 연기 살짝(분사 X), 측면에 작은 균열 표현 가능
- QA priority: medium

### bird-lose (새)

- Asset role: 패배 자세 - 날개 접고 가지에 앉은 듯 처진 모습
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/bird-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 91, vehicle 'bird' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/bird-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/bird-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 날개 접고 머리 숙임; col 1 = 깃털과 머리가 1px 움직임
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 파란/노란 작은 새, 양 날개 몸통에 붙임, 머리 살짝 숙임, 깃털 1개 떨어지는 효과
- QA priority: medium

### ninja-lose (닌자)

- Asset role: 패배 자세 - 한쪽 무릎 꿇고 검 거꾸로 든 닌자
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/ninja-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 1677, vehicle 'ninja' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/ninja-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/ninja-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 한쪽 무릎 꿇고 검을 거꾸로 듦; col 1 = 두건과 한숨 효과가 1px 움직임
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 검은 닌자복, 한쪽 무릎 꿇음, 두건 위 머리 약간 처짐, 표창/검은 거꾸로
- QA priority: medium

### boat-lose (배)

- Asset role: 패배 자세 - 가라앉기 시작한 배
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/boat-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 135, vehicle 'boat' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/boat-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/boat-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 한쪽으로 15도 기울어 가라앉기 시작함; col 1 = 거품이 움직이고 배가 1px 내려앉음
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 나무 보트, 한쪽으로 15도 기울어짐, 돛이 펄럭이지 않고 늘어짐, 작은 거품 옆에
- QA priority: normal

### bicycle-lose (자전거)

- Asset role: 패배 자세 - 자전거 옆으로 살짝 쓰러져 있고 라이더 한숨
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/bicycle-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 169, vehicle 'bicycle' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/bicycle-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/bicycle-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 자전거와 라이더가 10도 기울어짐; col 1 = 물방울과 고개가 1px 움직임
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 자전거가 약 10도 기울어짐, 라이더는 핸들 잡고 고개 숙임, 머리 위 물방울
- QA priority: normal

### scooter-lose (스쿠터)

- Asset role: 패배 자세 - 스쿠터 멈춤, 라이더 한숨
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/scooter-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 363, vehicle 'scooter' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/scooter-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/scooter-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 멈춘 스쿠터와 처진 라이더; col 1 = 헬멧 위 물방울이 1px 움직임
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 파란 스쿠터, 정지, 라이더 어깨 처짐, 헬멧 위에 물방울
- QA priority: normal

### helicopter-lose (헬리콥터)

- Asset role: 패배 자세 - 프로펠러 정지, 살짝 떨어지는 헬리콥터
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/helicopter-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 405, vehicle 'helicopter' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/helicopter-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/helicopter-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 프로펠러가 정지하고 5도 기울어짐; col 1 = 검은 연기와 차체가 1px 움직임
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 노란/검정 헬리콥터, 프로펠러 회전 X(정지), 살짝 비스듬히(5도), 작은 검은 연기
- QA priority: normal

### eagle-lose (독수리)

- Asset role: 패배 자세 - 날개 접고 시무룩한 독수리
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/eagle-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 315, vehicle 'eagle' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/eagle-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/eagle-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 날개 접고 고개 숙임; col 1 = 깃털과 한숨이 1px 움직임
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 갈색/검정 독수리, 양 날개 몸통에 붙임, 부리 닫고 시선 아래로, 깃털 약간 헝클어짐
- QA priority: normal

### crab-lose (게)

- Asset role: 패배 자세 - 집게 늘어뜨리고 옆으로 주저앉은 게
- Generation provider: OpenAI Images API
- Required image model: gpt-image-2
- Target file path: assets/horse-race/sprites/lose/crab-lose.png
- Source/reference path: D:\Work\LAMDiceBot\js\horse-race-sprites.js line 2027, vehicle 'crab' base svgMap run.frame1 state
- Animation tool path: output/horse-lose-poses-2026-05-05/tools/crab-lose.html
- Preview manifest path: output/horse-lose-poses-2026-05-05/manifests/crab-lose.json
- Asset type: sprite atlas (2-frame loop)
- Static image or sprite atlas: atlas
- Final canvas size: 120x45
- Grid columns: 2
- Grid rows: 1
- Cell size: 60x45
- Row meanings: row 0 = lose
- Column meanings: col 0 = 집게를 옆으로 늘어뜨리고 주저앉음; col 1 = 거품이 1px 움직이고 몸이 낮아짐
- Contact anchor: (30, 45) - feet/bottom at cell bottom
- Contact anchor meaning: track ground contact
- Y-axis baseline/source plane: cell bottom y=45 = track ground
- Player-readable purpose: mark the selected/penalty vehicle as disappointed during finish slow motion and result display
- Visual direction override: 빨간 게, 양 집게가 옆으로 늘어짐(위로 안 쳐듦), 다리 4개 살짝 굽힘, 머리 위 작은 거품
- QA priority: normal


