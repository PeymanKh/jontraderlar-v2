"""All user-facing Turkish copy lives here.

This is the single source of truth for what the bot says. Keeping it
separate from logic makes copy edits painless and keeps handlers clean.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Informational / instructional messages
# ---------------------------------------------------------------------------

class Info:
    WELCOME = (
        "<b>Jön Traderlar AI Botuna Hoş Geldin! 🤖</b>\n\n"
        "<b>Telegram topluluğumuza</b> katılmak için aşağıdaki adımları takip et:\n\n"
        "✅ <b>Adım 1:</b> <b>BingX</b> borsasına bu <a href=\"https://bingx.com/invite/JSLS8X/\"><b>referans linki</b></a> "
        "veya <b>ByBit</b> borsasına bu <a href=\"https://partner.bybit.com/b/5126\"><b>referans linki</b></a> ile kayıt ol.\n"
        "✅ <b>Adım 2:</b> Seçtiğin borsada <b>Kimlik Doğrulama (KYC)</b> işlemini tamamla.\n\n"
        "✅ <b>Adım 3:</b> <b>Bakiyeni</b> linkinden kayıt olduğun borsaya taşı ve gruba girebilmek ve grupta kalabilmek için "
        "artık bu borsaları kullanmaya devam et.\n"
        "✅ <b>Adım 4:</b> Borsada ilk işlemini yap. (Spot ya da kaldıraçlı işlem olabilir)\n\n"
        "Tüm adımları tamamladıktan sonra, uygunluğunu doğrulamak için <b>bana borsa UID'ni ve borsa adını</b> gönder.\n\n"
        "<b>Yardıma mı ihtiyacın var?</b> Hiç endişelenme! Bana dilediğin zaman sorularını sorabilirsin. 🙂\n\n"
        "<b>Unutmadan 😵‍💫:</b> Sadece gruba girmek için bu borsalara kayıt olup sonra <b>bakiyesini çekenler</b> "
        "yapay zeka tarafından tespit edilip <b>gruptan çıkarılır</b>."
    )

    SUPPORT = (
        "Destek ekibimize ulaşmak için aşağıdaki hesaplardan birine mesaj atabilirsiniz:\n\n"
        "👤 @trader_F777\n"
        "👤 @wolfsschanze34\n\n"
        "<i>Lütfen sorununuzu detaylı bir şekilde açıklayın, size en kısa sürede yardımcı olalım.</i>"
    )

    PROFILE = (
        "👤 <b>Doğrulanmış Hesaplarınız</b> 👤\n\n"
        "{account_list}\n"
        "📊 <i>Başarılı işlemleriniz devam etsin!</i>"
    )

    PROFILE_NOT_FOUND = (
        "❌ <b>Profil Bulunamadı</b> ❌\n\n"
        "Henüz sisteme kayıtlı değilsiniz. Doğrulama işlemini başlatmak için borsa adınızı ve UID'nizi gönderin.\n\n"
        "📝 <b>Format:</b> <code>borsa adı, UID</code>\n"
        "📝 <b>Örnek:</b> <code>bybit, 123456789</code>"
    )

    ACCOUNT_DETAIL = (
        "🏦 <b>{exchange_name}</b> - <b>UID:</b> <code>{exchange_uid}</code>\n"
        "📅 <b>Eklenme Tarihi:</b> {account_date}\n\n"
    )

    NO_ACCOUNTS = "   <i>Henüz bağlı hesap yok</i>"

    PROFILE_ERROR = (
        "❌ <b>Hata Oluştu</b> ❌\n\n"
        "Profil bilgileri alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin.\n\n"
        "Sorun devam ederse destek ekibiyle iletişime geçin."
    )

    CONFIRM_SECOND_ACCOUNT = (
        "<b>Telegram hesabınız zaten doğrulanmış.</b>\n\n"
        "Yeni bir hesap eklemek istiyor musunuz?\n"
        "<b>{exchange_name}</b> UID <code>{exchange_uid}</code>\n\n"
        "Lütfen <b>Evet</b> veya <b>Hayır</b> olarak yanıtlayın."
    )

    ACCOUNT_ADDED = (
        "🎉 <b>Başarılı!</b>\n\n"
        "<b>{exchange_name}</b> UID <code>{exchange_uid}</code> hesabınız profilinize eklendi.\n\n"
        "✅ Doğrulanmış borsalarınızı görmek için sol menüden <b>/hesaplarim</b> komutunu kullanabilirsiniz."
    )

    ACTION_CANCELLED = (
        "❌ İşlem iptal edildi.\n\n"
        "Başka bir konuda yardıma ihtiyacınız var mı?"
    )

    BINGX_KYC_CHANGE_1 = (
        "<b>🔄 BingX Kimlik Aktarma Rehberi</b>\n\n"
        "BingX üzerinde mevcut doğrulanmış hesabınızdaki kimlik bilgilerini başka bir hesaba aktarmak istiyorsanız, "
        "aşağıdaki şartları karşılamanız gerekir:\n\n"
        "<b>⚠️ Aktarma Öncesi Dikkat Edilmesi Gerekenler:</b>\n"
        "1. Sadece <b>Gelişmiş KYC</b> yapılmış hesaplar kimlik aktarımı yapabilir. <i>Temel KYC ile aktarma yapılamaz.</i>\n"
        "2. Kimlik aktarımı sonrasında hem mevcut hem de hedef hesap <b>180 gün boyunca</b> tekrar kimlik aktaramaz.\n"
        "3. Kimlik aktarımı yapılacak hesabın <b>doğrulanmamış (unverified)</b> olması gerekir.\n"
        "4. Aktarma sırasında <b>P2P işlemi veya ilanı</b> olan hesaplarda işlem yapılamaz. Önce bu işlemleri kapatmanız gerekir.\n"
        "5. <b>Anormal durumda</b> olan hesaplar bu işlemi gerçekleştiremez.\n"
        "6. Aktarım tamamlandığında mevcut hesabınız <b>unverified</b>, hedef hesabınız <b>verified</b> olur.\n"
        "7. Kimlik aktarımı sonrası eski hesap için <b>verilmemiş KYC ödülleri talep edilemez</b>."
    )

    BINGX_KYC_CHANGE_2 = (
        "<b>📱 Mobil Üzerinden:</b>\n"
        "1. BingX uygulamasına giriş yapın ve profil simgesine dokunun.\n"
        "2. <b>Doğrulama</b> sekmesine girin.\n"
        "3. <b>Kimlik Transferi</b> seçeneğine dokunun.\n"
        "4. Mevcut hesabın doğrulama bilgilerini girin ve hedef hesabı doğrulayarak işlemi tamamlayın.\n\n"
        "<b>💻 Web Üzerinden:</b>\n"
        "1. BingX web sitesine giriş yapın ve profilinize girin.\n"
        "2. <b>Kimlik Doğrulama</b> sekmesine tıklayın.\n"
        "3. <b>Kimlik Transferi</b> seçeneğini seçin.\n"
        "4. Mevcut hesabın bilgilerini girip hedef hesabı doğrulayın.\n\n"
        "<a href=\"https://bingx.com/en/support/articles/20877072634265/\">📎 Resmi Rehber</a>"
    )

    BYBIT_KYC_CHANGE_1 = (
        "<b>🔄 Bybit KYC Aktarma Rehberi</b>\n\n"
        "<b>Yeni bir hesaba KYC taşımak</b> için aşağıdaki adımları izlemeniz gerekir:\n\n"
        "1. <b>Mevcut hesabınızda KYC'yi tamamlayın</b> ve <b>24 saat</b> bekleyin.\n\n"
        "2. <b>Yeni bir hesap oluşturun</b> (veya daha önce oluşturduğunuz bir hesabı kullanın):\n"
        "  • Hesap <b>unverified</b> olmalı.\n"
        "  • İçinde <b>aktif pozisyon, bakiye ya da reklam</b> olmamalı.\n\n"
        "3. <b>Eski (mevcut) hesabınızdan:</b>\n"
        "  • Web veya uygulamada Profil → <b>Kimlik Doğrulama</b> kısmına girin.\n"
        "  • <b>Identity Transfer</b> bölümünü seçin."
    )

    BYBIT_KYC_CHANGE_2 = (
        "4. <b>Yeni hesabınızın</b> e-posta ya da telefon numarasını yazın.\n"
        "  • Her iki hesaba gelen kodları girerek doğrulama yapın.\n\n"
        "5. <b>Yüz tanıma</b> ve <b>güvenlik adımlarını</b> tamamlayın.\n\n"
        "6. <b>Aktarımı onaylayın:</b>\n"
        "  • KYC, yeni hesaba geçer.\n"
        "  • Eski hesap <b>unverified</b> olur.\n"
        "  • Her iki hesapta da <b>24 saatlik işlem kısıtı</b> uygulanır.\n\n"
        "<i>Any problem? Bybit destek ekibiyle iletişime geçebilirsiniz.</i>"
    )


# ---------------------------------------------------------------------------
# Success messages
# ---------------------------------------------------------------------------

class Success:
    VERIFICATION = (
        "🎉 <b>Doğrulama Başarılı!</b> 🎉\n\n"
        "✅ <b>KYC Kontrolü:</b> Tamamlandı\n"
        "✅ <b>Depozito Kontrolü:</b> Tamamlandı\n\n"
        "📊 <b>Risk Yönetimi Rehberi</b>\n"
        "Profesyonel trading için hazırladığımız rehberimizi mutlaka inceleyin:\n"
        "👉 <a href=\"https://drive.google.com/file/d/15FXMKGJDt1cZ5V9fL6xAEvLyB5m7MCmp/view?usp=drive_link\">"
        "Risk Yönetimi Kılavuzu</a>\n\n"
        "🔐 <b>Özel Grup Davetiniz</b>\n"
        "Tek kullanımlık davet linkiniz hazır!\n"
        "👉 <a href=\"{group_url}\">Jön Traderlar Grubuna Katıl</a>\n\n"
        "💰 <b>Başarılı işlemler ve bol kazançlar dileriz!</b>\n\n"
        "<i>💡 Not: Grup linki tek kullanımlık olup 24 saat geçerlidir.</i>"
    )


def verification_success_message(group_url: str) -> str:
    return Success.VERIFICATION.format(group_url=group_url)


# ---------------------------------------------------------------------------
# Error messages
# ---------------------------------------------------------------------------

class Errors:
    UNSUPPORTED_EXCHANGE = (
        "❌ <b>Desteklenmeyen borsa</b> ❌\n\n"
        "Lütfen <b>BingX</b> veya <b>ByBit</b> ile deneyin.\n"
        "<b>Örnek:</b> <code>bingx, 123456789</code>"
    )

    INVALID_UID_FORMAT = (
        "❌ <b>Geçersiz UID formatı</b> ❌\n\n"
        "UID sadece rakamlardan oluşmalıdır.\n"
        "<b>Örnek:</b> <code>bingx, 123456789</code>"
    )

    MISSING_VERIFICATION_DATA = (
        "Borsa hesabınızı doğrulamak ve özel telegram kanalına katılmak için, "
        "lütfen borsa adınızı ve UID'nizi bu formatta sağlayın.\n\n"
        "Lütfen şu formatta mesaj gönderin:\n"
        "<b>Format:</b> <code>borsa adı, UID</code>\n"
        "<b>Örnek:</b> <code>bingx, 123456789</code>"
    )

    BINGX_INVALID_UID = (
        "❌ <b>Geçersiz BingX UID</b> ❌\n\n"
        "Sağlanan UID mevcut değil veya BingX borsasında geçerli değil. Lütfen UID'nizi kontrol edin ve tekrar deneyin.\n\n"
        "Örnek format: <code>bingx, 123456789</code>"
    )

    BYBIT_INVALID_UID = (
        "❌ <b>Geçersiz ByBit UID</b> ❌\n\n"
        "Sağlanan UID mevcut değil veya ByBit borsasında geçerli değil. Lütfen UID'nizi kontrol edin ve tekrar deneyin.\n\n"
        "Örnek format: <code>bybit, 123456789</code>"
    )

    BINGX_WRONG_REFERRAL = (
        "❌ <b>BingX Hesabı Hirozaki Referansı İle Açılmamış</b> ❌\n\n"
        "Sağladığınız UID geçerli ancak hesabınız Hirozaki'nin referans kodu ile açılmamış.\n\n"
        "🔗 <b>Doğru kayıt için:</b>\n"
        "• Referans kodu: <code>JSLS8X</code>\n"
        "• Kayıt linki: <a href=\"https://bingx.com/invite/JSLS8X\">BingX'e Katıl</a>\n\n"
        "⚠️ <b>Önemli:</b> Sadece Hirozaki referansı ile kayıt olan kullanıcılar özel grubumuzda yer alabilir.\n\n"
        "💡 <b>Yanlış referans ile kayıt olduysanız:</b>\n"
        "Sol alttaki menüden <code>/bingx_kimlik_tasima</code> komutunu seçerek bu sorunu nasıl çözebileceğiniz hakkında "
        "bilgi alabilirsiniz."
    )

    BYBIT_WRONG_REFERRAL = (
        "❌ <b>ByBit Hesabı Hirozaki Referansı İle Açılmamış</b> ❌\n\n"
        "Sağladığınız UID geçerli ancak hesabınız Hirozaki'nin referans kodu ile açılmamış.\n\n"
        "🔗 <b>Doğru kayıt için:</b>\n"
        "• Referans kodu: <code>5126</code>\n"
        "• Kayıt linki: <a href=\"https://partner.bybit.com/b/5126\">ByBit'e Katıl</a>\n\n"
        "⚠️ <b>Önemli:</b> Sadece Hirozaki referansı ile kayıt olan kullanıcılar özel grubumuzda yer alabilir.\n\n"
        "💡 <b>Yanlış referans ile kayıt olduysanız:</b>\n"
        "Sol alttaki menüden <code>/bybit_kimlik_tasima</code> komutunu seçerek bu sorunu nasıl çözebileceğiniz hakkında "
        "bilgi alabilirsiniz."
    )

    KYC_NOT_COMPLETE = (
        "❌ <b>KYC doğrulaması tamamlanmamış</b> ❌\n\n"
        "Sağlanan UID geçerli ancak hesap KYC doğrulamasını tamamlamamış.\n"
        "Özel gruba katılabilmek için KYC doğrulaması gereklidir. Lütfen borsada kimlik doğrulamanızı tamamlayın ve tekrar deneyin."
    )

    NO_DEPOSIT_FOUND = (
        "❌ <b>Hesapta hiç işlem yapılmamış</b> ❌\n\n"
        "Sağlanan UID geçerli ancak bu hesapta hiç işlem yapılmamış. Lütfen en az 1 kez spot veya kaldıraçlı işlem açın.\n"
        "Borsa hesabınızı aktifleştirmek ve özel gruba katılabilmek için en az bir işlem yapmanız gerekmektedir."
    )

    EXCHANGE_UNKNOWN = (
        "⚠️ <b>Doğrulama sırasında bilinmeyen bir hata oluştu.</b>\n\n"
        "Borsa sunucusu beklenmeyen bir yanıt döndürdü.\n"
        "Lütfen birkaç dakika sonra tekrar deneyin veya destek ekibi ile iletişime geçin."
    )

    DATABASE_CONNECTION = (
        "⚠️ <b>Veritabanı bağlantı hatası</b> ⚠️\n\n"
        "Sunucu şu anda ulaşılamıyor. Geliştirici ekibine haber verdim, lütfen birkaç saat sonra tekrar deneyin."
    )

    DATABASE_OPERATION_FAILED = (
        "⚠️ <b>Kayıt işlemi başarısız</b> ⚠️\n\n"
        "Verileriniz kaydedilemedi. Geliştirici ekibine haber verdim, lütfen birkaç saat sonra tekrar deneyin."
    )

    DATABASE_UNKNOWN = (
        "⚠️ <b>Veritabanı hatası oluştu</b> ⚠️\n\n"
        "Beklenmeyen bir durum gerçekleşti.\n"
        "Geliştirici ekibine haber verdim, lütfen birkaç saat sonra tekrar deneyin."
    )

    USER_ALREADY_VERIFIED = (
        "<b>Telegram hesabınız daha önce bu borsa hesabına bağlanmış</b>\n\n"
        "Başka bir borsa hesabı bağlamak istiyorsanız, lütfen borsa adını ve UID'nizi şu formatta gönderin:\n\n"
        "<b>Format:</b> <code>borsa adı, UID</code>\n"
        "<b>Örnek:</b> <code>bybit, 123456789</code>"
    )

    EXCHANGE_ACCOUNT_ALREADY_USED = (
        "❌ <b>Bu borsa hesabı zaten doğrulanmış</b> ❌\n\n"
        "Bu UID başka bir Telegram hesabı tarafından kullanılıyor. Lütfen farklı bir UID deneyin."
    )

    INVITE_LINK_FAILED = (
        "⚠️ <b>Grup linki oluşturulamadı</b> ⚠️\n\n"
        "Telegram grup servisi şu anda ulaşılamıyor.\n"
        "Lütfen birkaç dakika sonra tekrar deneyin."
    )

    UNEXPECTED = (
        "⚠️ <b>Beklenmeyen bir hata oluştu</b> ⚠️\n\n"
        "Geliştirici ekibine haber verdim.\n"
        "Lütfen birkaç saat sonra tekrar deneyin."
    )

    BLOCKED_UID = (
        "❌ <b>Yanlış UID Gönderildi</b> ❌\n\n"
        "Gönderdiğin UID <b>Hirozaki'ye ait</b>. Gruba ekleyebilmem için lütfen <b>kendi UID'ini</b> gönder.\n\n"
        "📌 <b>Kendi UID'ini nasıl bulursun?</b>\n"
        "Ana sayfada sol üstteki <b>profil resmine</b> tıkla; açılan sayfada UID'in <b>sol en üstte</b> yazar."
    )


# ---------------------------------------------------------------------------
# Mappers from raw exchange / DB error strings to user-facing messages.
# ---------------------------------------------------------------------------

_EXCHANGE_BASE: dict[str, str] = {
    "kyc not complete": Errors.KYC_NOT_COMPLETE,
    "no deposit": Errors.NO_DEPOSIT_FOUND,
}

_EXCHANGE_SPECIFIC: dict[str, dict[str, str]] = {
    "bingx": {
        "invalid uid": Errors.BINGX_INVALID_UID,
        "wrong referral": Errors.BINGX_WRONG_REFERRAL,
    },
    "bybit": {
        "invalid uid": Errors.BYBIT_INVALID_UID,
        "wrong referral": Errors.BYBIT_WRONG_REFERRAL,
    },
}


def map_exchange_error(api_error: str | None, exchange: str | None) -> str:
    """Translate a raw exchange API error message to a Turkish user message."""
    if not api_error:
        return Errors.EXCHANGE_UNKNOWN

    if exchange:
        specific = _EXCHANGE_SPECIFIC.get(exchange.lower(), {})
        if api_error in specific:
            return specific[api_error]

    return _EXCHANGE_BASE.get(api_error, Errors.EXCHANGE_UNKNOWN)


_DATABASE: dict[str, str] = {
    "telegram account has been verified before": Errors.USER_ALREADY_VERIFIED,
    "exchange account is already verified for another user": Errors.EXCHANGE_ACCOUNT_ALREADY_USED,
    "database error occurred": Errors.DATABASE_UNKNOWN,
}


def map_database_error(db_error: str | None) -> str:
    if not db_error:
        return Errors.DATABASE_OPERATION_FAILED
    return _DATABASE.get(db_error, Errors.DATABASE_OPERATION_FAILED)
