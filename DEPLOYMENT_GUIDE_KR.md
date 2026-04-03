# VIBE BOX SPORTS 배포 가이드 (GitHub Pages)

이 프로젝트는 **stlite** 기술을 사용하여 서버 비용 없이 **GitHub Pages**에 무료로 배포할 수 있도록 설정되었습니다. 아래 단계를 따라 배포를 완료하세요.

## 1. 사전 준비
- 프로젝트가 GitHub 저장소에 업로드되어 있어야 합니다.
- 파일 구조에 `.github/workflows/static.yml`과 `generate_manifest.py`가 포함되어 있는지 확인하세요.

## 2. GitHub 저장소 설정
GitHub 웹사이트에서 다음 설정을 수행하세요:

1.  GitHub 저장소의 **Settings** 탭으로 이동합니다.
2.  왼쪽 메뉴에서 **Pages**를 클릭합니다.
3.  **Build and deployment** 섹션의 **Source** 드롭다운 메뉴에서 `GitHub Actions`를 선택합니다.
    - *참고: `Deploy from a branch`가 아닌 `GitHub Actions`를 선택해야 합니다.*

## 3. 배포 실행
1.  로컬에서 변경 사항을 저장하고 GitHub로 `push`합니다.
2.  저장소의 **Actions** 탭으로 이동하면 `Deploy to GitHub Pages` 워크플로우가 실행되는 것을 볼 수 있습니다.
3.  워크플로우가 성공적으로 완료되면 **Settings > Pages** 탭 상단에 배포된 사이트 URL이 표시됩니다.

## 4. 업데이트 방법
- 새로운 데이터를 추가하거나 코드를 수정한 후 GitHub에 `push`하기만 하면 됩니다.
- GitHub Actions가 자동으로 `generate_manifest.py`를 실행하여 새로운 `stlite-manifest.json`을 생성하고 사이트를 업데이트합니다.

---

> [!WARNING]
> **데이터 저장 관련 주의사항**:
> 이 배포 방식은 브라우저에서 실행되는 방식이므로, 사용자가 작성한 **게시판 글이나 문의 내역은 서버에 저장되지 않으며** 페이지를 새로고침하면 사라집니다. (예측 엔진 및 통계 기능은 정상 작동합니다.)

> [!TIP]
> **HTTPS 지원**: GitHub Pages는 기본적으로 HTTPS를 지원하므로 보안 연결이 보장됩니다.
