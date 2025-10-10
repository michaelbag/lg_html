# Инструкция по размещению на GitHub

## Шаг 1: Создайте репозиторий на GitHub

1. Откройте https://github.com/new
2. Repository name: `lg_html`
3. Description: `Генератор этикеток с DataMatrix кодами`
4. **НЕ** ставьте галочки на "Add a README file", "Add .gitignore", "Choose a license"
5. Нажмите "Create repository"

## Шаг 2: Выполните команды в терминале

```bash
# Перейдите в директорию проекта
cd /Users/mihailkudravcev/Projects/lg_html

# Добавьте все файлы в git
git add .

# Создайте первый коммит
git commit -m "Initial commit: Label generator with DataMatrix codes

- Генерация этикеток из CSV
- Поддержка PDF/JPG шаблонов
- Высокое разрешение для текста (1200 DPI)
- Исправлено наложение текста на страницах
- Конфигурация через JSON/INI
- Прозрачный фон для PNG"

# Переименуйте ветку в main (если нужно)
git branch -M main

# Добавьте удаленный репозиторий
git remote add origin https://github.com/michaelbag/lg_html.git

# Отправьте код на GitHub
git push -u origin main
```

## Шаг 3: Настройте аутентификацию (если потребуется)

Если GitHub запросит аутентификацию, используйте один из способов:

### Вариант А: Personal Access Token (рекомендуется)

1. Перейдите на https://github.com/settings/tokens
2. Нажмите "Generate new token" → "Generate new token (classic)"
3. Выберите срок действия и разрешения: `repo` (полный доступ к приватным репозиториям)
4. Нажмите "Generate token"
5. Скопируйте токен (он больше не появится!)
6. При запросе пароля введите токен вместо пароля

### Вариант Б: SSH ключ

```bash
# Проверьте наличие SSH ключа
ls -al ~/.ssh

# Если ключа нет, создайте новый
ssh-keygen -t ed25519 -C "your_email@example.com"

# Добавьте ключ в ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Скопируйте публичный ключ
cat ~/.ssh/id_ed25519.pub

# Добавьте ключ на GitHub:
# https://github.com/settings/keys → "New SSH key"
```

Затем измените remote URL на SSH:

```bash
git remote set-url origin git@github.com:michaelbag/lg_html.git
git push -u origin main
```

## Шаг 4: Проверьте результат

Откройте https://github.com/michaelbag/lg_html и убедитесь, что все файлы загружены.

## Дополнительно: Создание релиза

После успешного push:

1. Перейдите на страницу репозитория
2. Нажмите "Releases" → "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: `v1.0.0 - Initial Release`
5. Описание релиза (можно скопировать из README)
6. Нажмите "Publish release"

## Полезные команды

```bash
# Проверка статуса
git status

# Просмотр истории
git log --oneline

# Проверка remote
git remote -v

# Добавление новых изменений
git add .
git commit -m "Описание изменений"
git push
```
