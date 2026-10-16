# K1 혼자 줄넘기 — 시뮬 타당성 검토 (2026-10-16)

페이지: https://chanyong0211.github.io/k1-jump-rope/

K1 휴머노이드가 스스로 줄을 돌리며 넘을 수 있는지 MuJoCo 시뮬로 확인한 결과 정리입니다. 영상은 `media/`에 있습니다.
GitHub Pages 에서는 "고치기"로 편집한 뒤 저장하면 고친 `index.html` 을 내려받기만 합니다.

## 페이지 고치기

```
git clone https://github.com/chanyong0211/k1-jump-rope
cd k1-jump-rope
git pull
python3 docs_server.py        # http://localhost:8098/ 에서 "고치기" → 고친 뒤 "저장"
git commit -am "페이지 판 N"
git push
```

- 고치기 전에 꼭 `git pull`. 두 곳에서 동시에 고치면 나중 push 가 거절되고 충돌을 손으로 풀어야 한다.
- 저장할 때마다 이전 판이 `doc_backups/` 에 남는다(git 에는 안 올라감). 옛 판 위에서 고친 저장은 거절된다(409).
- 저장 전 편집은 브라우저 초안으로 남는다. 페이지를 다시 열면 초안 불러오기·버리기를 묻는다.
- 그림·영상 자체는 페이지에서 못 바꾼다(설명 글만). 영상을 바꾸려면 `media/` 파일을 바꾸고 commit 한다.
