루멘콘덴서 계산기 - 캐릭터 이미지 폴더
=====================================

이 폴더에 이미지를 넣으면 계산기가 자동으로 사용합니다.
파일이 없으면 캐릭터 색으로 만든 대체 그림이 나옵니다.

파일 이름 규칙:  {캐릭터id}_{종류}.png   (.webp 도 가능)

  종류
  - body  : 전신 (캐릭터 선택 화면 좌/우). 배경 투명 PNG 권장, 세로로 긴 비율
  - face  : 두상 (선택 화면 마름모 칸, 계산기 이름표). 정사각형, 얼굴이 가운데.
            그림을 시계 반대방향으로 45° 돌려 넣은 정사각형 → 앱이 시계방향 45°로 되돌려
            정사각형 전체가 마름모 칸을 꽉 채움 (네 귀퉁이 = 마름모의 위·오른쪽·아래·왼쪽 꼭짓점)
  - trait : 특성 마크 (계산기 하단 특성 ON/OFF). 정사각형 권장, 마름모로 잘려 보임

  예)  wolf_body.png   wolf_face.png   wolf_trait.png

  리타 상태 일러(정사각형): rita_guardian.png / rita_assassin.png / rita_paladin.png
  타오 토큰 일러(정사각형): tao_yang.png (양) / tao_yin.png (음)
  (리타의 trait 이미지 = 빛의 루멘, 타오의 trait 이미지 = 조화)

캐릭터 id 목록
  니아          nia
  루트          root
  델피          delphi
  키스 더 래빗  kiss
  울프          wolf
  비올라        viola
  레브          rev
  타오          tao
  리타          rita
  린            lin
  요한          johan
  이제벨        jezebel
  이오몽        iomong
  키메라        chimera
  무영          muyoung
  핀프          finf
  CMYK          cmyk
  미녕이        minyeong

새 캐릭터 추가
  1) lumencalc.html 의 CHARACTERS 목록에 한 줄 추가
       { id: 'newchar', name: '새캐릭터' },
     체력·손패·토큰이 다르면:
       { id: 'newchar', name: '새캐릭터', hp: 4500, hands: [6, 7, 8, 9, 9], token: { label: '토큰이름', max: 3 } },
  2) 이 폴더에 newchar_body.png / newchar_face.png / newchar_trait.png 넣기
