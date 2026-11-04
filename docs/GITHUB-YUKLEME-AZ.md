# Layihəni GitHub-a yükləmək — addım-addım

## 1. Hazırlıq (bir dəfəlik)

1. github.com-da hesab aç. İstifadəçi adı peşəkar olsun, məsələn `jamilqarahmadov`.
2. Kompüterinə Git quraşdır: https://git-scm.com/downloads
3. Terminalda adını və e-poçtunu təyin et:

```bash
git config --global user.name "Jamil Qarahmadov"
git config --global user.email "cemil.qarahmedov@gmail.com"
```

## 2. GitHub-da boş repo yarat

GitHub → sağ yuxarıda **+** → **New repository**
- Ad: `secure-cicd-pipeline`
- **Public** seç
- README, .gitignore, license əlavə ETMƏ (onlar artıq layihədədir)

## 3. Faylları yüklə

Zip-i aç, terminalda həmin qovluğa keç:

```bash
cd secure-cicd-pipeline
git init
git add .
git commit -m "Secure CI/CD pipeline with security gates"
git branch -M main
git remote add origin https://github.com/ISTIFADECI_ADIN/secure-cicd-pipeline.git
git push -u origin main
```

Parol soruşanda GitHub hesab parolu işləmir: **Settings → Developer settings → Personal access tokens** bölməsindən token yarat və onu yapışdır. Və ya daha asan yol: GitHub Desktop proqramını istifadə et.

## 4. Pipeline-ın işlədiyini yoxla

Repo-da **Actions** tabına keç. Pipeline avtomatik başlayacaq. Bütün gate-lər yaşıl olmalıdır.

## 5. README-də iki yeri düzəlt

- `OWNER` sözünü GitHub istifadəçi adınla əvəz et (badge işləsin)
- `[LinkedIn](#)` yerinə LinkedIn linkini qoy

## 6. Demo üçün: gate-in işlədiyini göstər

Müsahibədə ən təsirli an budur. Yeni branch aç, `app/main.py`-ın sonuna `app.run(debug=True)` yaz, Pull Request aç. Semgrep pipeline-ı dayandıracaq. Bunun ekran görüntüsünü README-yə əlavə et və ya müsahibədə canlı göstər.

## Müsahibədən əvvəl

Hər faylı açıb hər sətrin nə etdiyini öz sözlərinlə izah edə bilməlisən. Bilmədiyin yer olsa, soruş, birlikdə keçək.
