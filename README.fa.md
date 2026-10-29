# جادو (Jadu)

مجموعه‌ای از workflowهای آماده برای agentهای هوش مصنوعی، مخصوص جلسات کاری ساختارمند و پربازده. ریپو را فورک کنید، workflowهای موردنیاز را در پروژه‌تان کپی کنید، و از آن‌ها در Claude Code یا Codex استفاده کنید.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## workflowهای موجود

| workflow | Claude Code | Codex | کارایی |
|---|---|---|---|
| Bidar | `/jadu-bidar` | skill `jadu-bidar` | شروع جلسه — وضعیت پروژه را می‌خواند و زیروظایف برنامه‌ریزی را کامل‌تر می‌کند |
| Zad | `/jadu-zad` | skill `jadu-zad` | ویزارد راه‌اندازی پروژه — سوالات را یک‌جا می‌پرسد و فایل‌های context پروژه را می‌سازد |
| Payan | `/jadu-payan` | skill `jadu-payan` | پایان جلسه — بدون خلاصه، به‌صورت مستقیم مستندات/وظایف را به‌روزرسانی می‌کند و در پایان به‌طور خودکار commit و push می‌کند |
| Loop | `/jadu-loop` | skill `jadu-loop` | **اختیاری و به‌صورت پیش‌فرض خاموش.** اجرای خودکار زیروظایف از‌پیش‌تاییدشده در `LOOP_TASK.md` — بدون تاییدِ هر مرحله. به بخش «راه‌اندازی Loop» پایین مراجعه کنید |
| Loop (best practice) | `/jadu-loop-best-practice` | skill `jadu-loop-best-practice` | **اختیاری و به‌صورت پیش‌فرض خاموش.** مثل Loop، اما به‌جای توقف برای انسان، بهترین تصمیم را می‌گیرد، ثبتش می‌کند و ادامه می‌دهد؛ همه‌ی تصمیم‌ها را در PR بررسی می‌کنید. به بخش «نسخه‌ی best practice» پایین مراجعه کنید |
| Loop prepare | `/jadu-loop-prepare` | skill `jadu-loop-prepare` | تسک‌های موجود پروژه (فایل‌های فاز، plan، کارهای باقی‌مانده) را به فایل‌های تسک آماده در `LOOP_TASK_QUEUE/` برای loop نسخه‌ی best practice تبدیل می‌کند. فقط آماده می‌کند و loop را اجرا نمی‌کند |

`jadu-tamam` به `jadu-payan` تغییر نام داده است.

---

## نحوه استفاده

### Claude Code

دستورهای موردنیاز را در دایرکتوری `.claude/commands/` پروژه‌تان کپی کنید:

```bash
cp .claude/commands/jadu-bidar.md /your-project/.claude/commands/
```

یا همه دستورهای Claude Code را به‌صورت سراسری نصب کنید:

```bash
mkdir -p ~/.claude/commands
cp .claude/commands/jadu-*.md ~/.claude/commands/
```

### Codex

فولدرهای skill موردنیاز را در پروژه یا مسیر skillهای Codex کپی کنید:

```bash
mkdir -p ~/.codex/skills
cp -R .codex/skills/jadu-* ~/.codex/skills/
```

سپس یک جلسه جدید Codex باز کنید و workflow را با نامش صدا بزنید؛ مثلاً `jadu-bidar`.

### راهنمای مشترک پروژه

برای پروژه‌هایی که چند agent دارند، فایل `AGENTS.md` را در ریشه پروژه نگه دارید. workflowهای Codex در جادو، `AGENTS.md` را منبع اصلی دستورالعمل‌ها می‌دانند. برای Claude Code می‌توانید یک `CLAUDE.md` کوچک نگه دارید که به راهنمای مشترک اشاره کند.

---

## جریان پیشنهادی جلسه

1. `jadu-zad` — ساخت یا به‌روزرسانی فایل‌های context پروژه.
2. `jadu-bidar` — شروع جلسه، pull امن، خواندن context و انتخاب تمرکز.
3. `jadu-payan` — بستن مستقیم جلسه، به‌روزرسانی مستندات/وظایف، و سپس commit و push خودکار.
4. درخواست صریح `push` — commit و push در هر زمانی جز لحظه بستن جلسه.

---

## راه‌اندازی Loop (اختیاری)

`jadu-loop` با سه workflow دیگر فرق دارد: تنها استثنای عمدی روی قاعده‌ی «هیچ‌وقت بدون سیگنال صریح پیاده‌سازی نکن» است، پس به چند تکه‌ی اضافه و یک فایل تسک که یک انسان نوشته باشه نیاز داره تا اصلاً بتونه اجرا بشه. فقط با کپی‌کردن `jadu-loop.md`/فولدر skill آن، هیچ چیزی به‌صورت خودکار فعال نمی‌شود.

1. مثل بقیه‌ی workflowها دستور/skill را کپی کنید (بخش «نحوه استفاده» بالا).
2. اسکریپت‌های پشتیبان را کپی کنید: `cp -R scripts/jadu-loop /your-project/scripts/` — برای اینکه هر کدام چیکار می‌کنند و چطور نصب می‌شوند (وابستگی `python-dotenv` و در صورت تمایل نوتیفیکیشن Telegram) به [`scripts/jadu-loop/README.md`](scripts/jadu-loop/README.md) مراجعه کنید.
3. یک `LOOP_TASK.md` در ریشه‌ی پروژه‌تان از روی [`templates/jadu-loop/LOOP_TASK.skeleton.md`](templates/jadu-loop/LOOP_TASK.skeleton.md) بسازید، یا از نمونه‌ی کامل [`templates/jadu-loop/LOOP_TASK.example.md`](templates/jadu-loop/LOOP_TASK.example.md) شروع کنید.
4. **قبل از نوشتن اولین تسک واقعی، حتماً [`docs/jadu-loop-authoring-guide.md`](docs/jadu-loop-authoring-guide.md) را بخوانید.** هر قانون آن مربوط به یک باگ واقعی است که در یک اجرای بدون‌نظارت رخ داده — کوتاه است، و نخواندنش یعنی همان باگ‌ها دوباره تکرار می‌شوند.
5. یک دایرکتوری tracked به نام `LOOP_TASK_ARCHIVE/` بسازید (فایل‌های تسک تمام‌شده به آن‌جا منتقل می‌شوند) و `.loop_state/` را gitignore کنید (فقط وضعیت محلی اجرا).
6. قبل از اجرای loop، هر دستوری که زیروظایف‌تان اجرا می‌کنند را به allowlist شل agentتان اضافه کنید — loop نمی‌تواند مجوزهای خودش را وسط اجرا گسترش دهد.
7. اجرا کنید: `python3 scripts/jadu-loop/check_loop_queue.py && python3 scripts/jadu-loop/check_usage_margin.py && claude -p "/jadu-loop" --permission-mode acceptEdits` — دستی، یا داخل یک حلقه‌ی خودتان (`while ... sleep N; done`) برای یک تسک طولانی و بدون‌نظارت. **بدون تصمیم صریح، این را به `cron` وصل نکنید** — به یادداشت‌های مربوط به `cron` در بخش سفارشی‌سازی/راهنمای مشترک مراجعه کنید. برای یک اجرای طولانی و بدون‌نظارت، `python3 scripts/jadu-loop/run_loop.py` حلقه را خودش اجرا می‌کند: به‌جای مصرف اعتبار اضافه (usage credits)، صبر می‌کند تا سقف ۵ساعته/هفتگی ریست شود و بعد ادامه می‌دهد (به `scripts/jadu-loop/README.md` مراجعه کنید).

### نسخه‌ی best practice (اختیاری)

`jadu-loop-best-practice` همان راه‌اندازی، همان فایل‌های تسک و همان اسکریپت‌ها را استفاده می‌کند. تفاوتش این است: هر جا که `jadu-loop` می‌ایستد و منتظر شما می‌ماند (یک `review-checkpoint`، یک `VERIFY` که مدام شکست می‌خورد، یک انتخاب طراحی، یک زیروظیفه‌ی مبهم، یک تسک تمام‌شده)، این نسخه بهترین تصمیم را می‌گیرد، آن را در بخش `## Decisions` فایل `LOOP_TASK.md` ثبت می‌کند و ادامه می‌دهد. شما همه چیز را یک‌جا در PR بررسی می‌کنید: زیروظیفه‌ای که بعد از سه تلاش هنوز شکست می‌خورد کنار گذاشته می‌شود و PR به‌صورت draft باز می‌شود، با فهرست تصمیم‌ها و زیروظایف کنارگذاشته‌شده در متن آن. محدودیت‌های سخت همچنان متوقفش می‌کنند: هیچ‌وقت merge نمی‌کند، به trunk push نمی‌کند، به production یا secretها دست نمی‌زند و مجوزهای خودش را گسترش نمی‌دهد.

- مثل `jadu-loop` نصبش کنید (مرحله‌ی ۱ بالا). اگر `/jadu-loop-best-practice` را در چت بنویسید، `scripts/jadu-loop/run_loop.py` را در پس‌زمینه اجرا می‌کند و همان‌جا دنبالش می‌کند: برای هر تسک یک `claude -p "/jadu-loop-best-practice --task"` تازه. اجرای یک تسک با دست: `claude -p "/jadu-loop-best-practice --task" --model opus --permission-mode acceptEdits`.
- هر زیروظیفه ۲۰ دقیقه وقت دارد؛ اجرایی که ۳۰ دقیقه هیچ commitی نداشته باشد را runner متوقف می‌کند و زیروظیفه‌اش علامت `TIMEOUT 1` (دوباره امتحان می‌شود) یا `TIMEOUT 2` (کنار گذاشته می‌شود) می‌گیرد.
- مجوزهای دائمی: کارهای مخصوص مالک را که از قبل تأیید می‌کنید در `.claude/loop-grants.md` بنویسید (`install`، `allowlist`، `security-patch`، `advance`). محدودیت‌های سخت هیچ‌وقت مجوز نمی‌گیرند.
- برای این نسخه، `LOOP_TASK.md`، `LOOP_TASK_QUEUE/`، `LOOP_TASK_ARCHIVE/`، `.loop_state/` و `.claude/loop-grants.md` را به‌جای آرشیو tracked مرحله‌ی ۵ gitignore کنید تا صف با عوض‌شدن branch از بین نرود و وارد PR نشود. آرشیو tracked هم کار می‌کند؛ loop جابه‌جایی را روی branch تسک commit می‌کند. `LOOP_TASK.md` و `LOOP_TASK_QUEUE/` را هرگز روی trunk commit نکنید: loop بعد از هر تسک به trunk برمی‌گردد، نسخه‌ی commit‌شده با آن برمی‌گردد و تسک تمام‌شده دوباره اجرا می‌شود.
- صف اختیاری: فایل‌های تسک آماده‌ی بعدی را در `LOOP_TASK_QUEUE/` بگذارید. وقتی PR یک تسک باز شد و آن تسک بایگانی شد، فایل بعدی (به ترتیب نام) به `LOOP_TASK.md` تبدیل می‌شود و اجرای بعدی آن را شروع می‌کند.
- اگر Briefing بگوید پروژه‌تان production را چطور مشخص می‌کند (مثلاً خط `ENVIRONMENT=`)، loop اول آن را چک می‌کند و روی production اجرا نمی‌شود.

---

## سفارشی‌سازی

- **تغییر پیشوند** — پیشوند `jadu-` اختیاری است. فایل‌ها را به هر نامی که دوست دارید تغییر دهید (`/start`، `/push`، `/done`) و Claude Code نام‌های جدید را تشخیص خواهد داد.
- **ویرایش workflow** — هر دستور یا skill یک Markdown ساده است. مراحل، لحن، یا ساختار را متناسب با جریان کاری خود تغییر دهید.
- **هماهنگ نگه داشتن agentها** — اگر رفتار workflow تغییر کرد، هم `.claude/commands/` و هم `.codex/skills/` را به‌روزرسانی کنید.
- **اضافه کردن workflow جدید** — برای Claude Code یک فایل `.md` در `.claude/commands/` بسازید؛ برای Codex یک فولدر `.codex/skills/<name>/SKILL.md` بسازید.

---

## مشارکت

PR خوش‌آمد است. هنگام تغییر رفتار workflowها، دستورهای Claude Code، skillهای Codex و مستندات کاربر را هماهنگ نگه دارید.
