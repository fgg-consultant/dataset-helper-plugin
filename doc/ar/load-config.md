# تحميل ملف JSON

يخدم زر **Load Config JSON** غرضين متميزين:

1. **معاينة الكتالوج المدمج** المسلَّم مع المكوّن (إجراء *Review embedded catalog*).
2. **تحميل JSON مخصص** تلصقه في منطقة النص.

في كلتا الحالتين، يملأ التحميل جدول `CatalogEntry` أو يحدّثه. **لا يُنشأ أي كائن Climweb حتى تنقر على *Synchronize with Climweb***.

## الكتالوج المدمج (الحالة القياسية)

راجع الصفحة المخصصة [تحديثات الكتالوج](./updates). التدفق العادي هو:

1. **Review embedded catalog** → ترى الفرق بين JSON على القرص وكتالوج القاعدة.
2. **Apply changes** → يُحدَّث جدول `CatalogEntry`، ويذكر `CatalogState` الإصدار.
3. **Synchronize with Climweb** → تُنشأ / تُحذف / تُحدَّث كائنات `Dataset` في Climweb.

## JSON مخصص

إذا كنت تدير ملف الكتالوج الخاص بك (بالإضافة إلى الكتالوج المدمج أو بدلاً منه)، الصق محتواه في منطقة النص وانقر على **Load into Catalog**.

يقوم المكوّن بـ:

- إنشاء المدخلات المفقودة،
- تحديث تلك التي تغير محتواها،
- ترك الباقي كما هو.

تحمل المدخلات التي يتم إنشاؤها بهذا المسار الأصل **`config`**، مثل تلك الموجودة في الكتالوج المدمج. عاقبة مهمة: إذا حمّلت الكتالوج المدمج لاحقًا، فإن مدخلات `config` التي لا تظهر في JSON المدمج ستُكتشف على أنها **`to remove`** بواسطة المعاينة. لذا فإن مزج عدة مصادر `config` يتطلب بعض الانتباه.

## التنسيق المتوقع

يجب أن يتبع JSON البنية المتداخلة **Categories → Subcategories → Datasets → Layers**:

```json
{
  "version": "2026.05.18",
  "schema_version": 1,
  "categories": [
    {
      "title": "Rainfall",
      "icon": "raindrops",
      "subcategories": [
        {
          "title": "Observation",
          "datasets": [
            {
              "title": "10-day precipitation estimate",
              "description": "...",
              "multi_temporal": true,
              "public": true,
              "metadata": {
                "function": "...",
                "resolution": "0.05deg",
                "source": "JRC eStation",
                "geographic_coverage": "Africa",
                "license": "Open Data",
                "frequency_of_update": "Dekadal",
                "overview": "...",
                "learn_more": "https://..."
              },
              "layers": [
                {
                  "type": "wms",
                  "title": "RFE 10-day",
                  "layer_name": "rfe_10d",
                  "wms_url": "https://example.org/wms",
                  "default": true
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

الحقول الجذرية:

| الحقل              | الدور                                                                          |
|--------------------|--------------------------------------------------------------------------------|
| `version`          | معرّف إصدار الكتالوج. يُستخدم لاكتشاف التحديثات.                              |
| `schema_version`   | إصدار مخطط JSON. يزداد عندما يتغير شكل المدخلات.                               |
| `categories[]`     | قائمة الفئات في أعلى المستوى.                                                  |

للسلاسل متعددة اللغات، يستخدم الكتالوج المدمج قاموسًا `{ "en": "...", "fr": "...", … }`. يختار المكوّن اللغة المكوّنة في [الإعدادات](./settings) عند التحميل. تُقبل أيضًا سلسلة بسيطة.

## أنواع الطبقات المدعومة

يمكن أن يأخذ الحقل `type` داخل `layers[]` القيم التالية:

- `wms` — خدمة WMS قياسية (الأكثر شيوعًا).
- `raster_tile` / `vector_tile` — خدمات بلاط XYZ أو PMTiles.
- `raster_file` / `vector_file` — ملفات قابلة للتنزيل (مع مصادقة Bearer اختيارية).
- `raster_cog` — Cloud-Optimized GeoTIFF مع قالب زمني.

كل نوع له حقوله الخاصة (قالب URL، الفاصل الزمني، نمط raster، تكوين النوافذ المنبثقة…). راجع الكتالوج المدمج للحصول على أمثلة كاملة.
