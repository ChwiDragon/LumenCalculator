루멘 카운터 - 캐릭터 이미지 폴더
=====================================

이 폴더에 이미지를 넣으면 계산기가 자동으로 사용합니다.
파일이 없으면 캐릭터 색으로 만든 대체 그림이 나옵니다.

파일 이름 규칙:  {캐릭터id}_{종류}.png   (.webp 도 가능)

  종류
  - body  : 반신 (캐릭터 선택 화면 좌/우, 선택 칸 뒤). 정사각형 1000×1000, 배경 투명 PNG/WebP 권장.
            그림 위에서 14% 지점을 앱이 화면 높이 55%에 맞춤. 모서리는 둥글게, 네 변은 흐리게 사라짐
            (좌우 14%, 위 12%, 아래 28%) → 중요한 부분은 가운데에
  - face  : 두상 (선택 화면 마름모 칸, 계산기 이름표). 정사각형, 얼굴이 가운데.
            그림을 시계 반대방향으로 45° 돌려 넣은 정사각형 → 앱이 시계방향 45°로 되돌려
            정사각형 전체가 마름모 칸을 꽉 채움 (네 귀퉁이 = 마름모의 위·오른쪽·아래·왼쪽 꼭짓점)
  - trait : 특성 마크 (계산기 하단 특성 ON/OFF). 정사각형 권장, 마름모로 잘려 보임

  예)  wolf_body.png   wolf_face.png   wolf_trait.png

  추가 일러스트 (선택 사항): body2 / face2 (이오몽 두상은 face3, CMYK 두상은 face3 / face4 까지)
  - 앱 설정 > 일러스트 탭에서 캐릭터마다 반신·두상 버튼을 눌러 일러스트 고르기 창에서 고름.
  - 고른 번호의 파일이 없으면 1번(body / face)으로 보임. 크기·규칙은 1번과 같음.
  - 1번과 똑같은 파일은 빌드 때 지워짐(app/optimize-art.py). 고르기 창에는 실제로 있는 그림만 나옴.
  예)  wolf_body2.webp   wolf_face2.webp   iomong_face3.webp   cmyk_face3.webp   cmyk_face4.webp

  리타 상태 일러(정사각형): rita_guardian.png / rita_assassin.png / rita_paladin.png
  타오 토큰 일러(정사각형): tao_yang.png (양) / tao_yin.png (음)
  (리타의 trait 이미지 = 빛의 루멘, 타오의 trait 이미지 = 조화)

캐릭터 id 목록
  니아          nia
  루트          root
  델피          delphi
  키스          kiss
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
  부쿠키        bukuki

용량
  빌드 때 app/optimize-art.py 가 그림을 손실 WebP(품질 80)로 다시 저장함(10% 이상 줄 때만).
  바꾸기 전 원본은 release/asset-backup/characters-orig/ 에 남음.

새 캐릭터 추가
  1) lumencalc.html 의 CHARACTERS 목록에 한 줄 추가
       { id: 'newchar', name: '새캐릭터' },
     체력·손패·토큰이 다르면:
       { id: 'newchar', name: '새캐릭터', hp: 4500, hands: [6, 7, 8, 9, 9], token: { label: '토큰이름', max: 3 } },
  2) 이 폴더에 newchar_body.png / newchar_face.png / newchar_trait.png 넣기
