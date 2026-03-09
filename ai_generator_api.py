import os
import random
from openai import OpenAI
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from dotenv import load_dotenv

load_dotenv()
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
try:
    vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_LOCATION"))
    imagen_model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    print("Imagenモデルのロード完了")
except Exception as e:
    print(f"Google Cloudの初期化に失敗しました: {e}")
    imagen_model = None

# ▼▼▼ MARK_DEFINITIONS に 'display_name_en' を追加 ▼▼▼
MARK_DEFINITIONS = {
    "Planner": {"file": "mark_planner.png", "display_name": "計画性", "display_name_en": "Planner"},
    "Spontaneous": {"file": "mark_spontaneous.png", "display_name": "自発性", "display_name_en": "Spontaneous"},
    "Outgoing": {"file": "mark_outgoing.png", "display_name": "外交的", "display_name_en": "Outgoing"},
    "Reserved": {"file": "mark_reserved.png", "display_name": "控えめ", "display_name_en": "Reserved"},
    "Introvert": {"file": "mark_introvert.png", "display_name": "内向的", "display_name_en": "Introvert"},
    "Extrovert": {"file": "mark_extrovert.png", "display_name": "外向的", "display_name_en": "Extrovert"},
    "Logical": {"file": "mark_logical.png", "display_name": "論理的", "display_name_en": "Logical"},
    "Intuitive": {"file": "mark_intuitive.png", "display_name": "直感的", "display_name_en": "Intuitive"},
    "Present-focused": {"file": "mark_present.png", "display_name": "現在志向", "display_name_en": "Present-focused"},
    "Future-oriented": {"file": "mark_future.png", "display_name": "未来志向", "display_name_en": "Future-oriented"},
    "Decisive": {"file": "mark_decisive.png", "display_name": "決断力", "display_name_en": "Decisive"},
    "Deliberate": {"file": "mark_deliberate.png", "display_name": "慎重派", "display_name_en": "Deliberate"},
    "Creative": {"file": "mark_creative.png", "display_name": "創造性", "display_name_en": "Creative"},
    "Analytical": {"file": "mark_analytical.png", "display_name": "分析的", "display_name_en": "Analytical"},
    "Empathetic": {"file": "mark_empathetic.png", "display_name": "共感的", "display_name_en": "Empathetic"},
    "Independent": {"file": "mark_independent.png", "display_name": "自立性", "display_name_en": "Independent"},
}
# ▲▲▲ ここまで ▲▲▲


def analyze_personality(data):
    """回答データから性格特性キーワード、成分、マークを導き出す"""
    lang = data.get('lang', 'ja')
    
    personality_explicit = [d for d in data['explicit'] if d.get('type') == 'personality']
    personality_implicit = [d for d in data['implicit'] if d.get('type') == 'personality']

    if not personality_explicit:
        raise ValueError("性格分析のためのデータがありません。")

    answers = [item["answer"] for item in personality_explicit]
    times = [item["time"] for item in personality_implicit]
    avg_time = sum(times) / len(times)
    
    components = {"内向性": 50, "直感性": 50, "計画性": 50, "協調性": 50, "論理性": 50, "感受性": 50}
    trait_keywords = []

    # Q1: 計画性 (変更なし)
    if answers[0] == 'yes':
        components["計画性"] += 30; trait_keywords.append("Planner")
    else:
        components["計画性"] -= 30; trait_keywords.append("Spontaneous")
    
    # Q2: 内向/外向 (変更なし)
    if answers[1] == 'yes':
        components["内向性"] += 30; trait_keywords.append("Reserved")
    else:
        components["内向性"] -= 20; trait_keywords.append("Outgoing")

    # Q3: 内向/外向 (変更なし)
    if answers[2] == 'yes':
        components["内向性"] += 30; trait_keywords.append("Introvert")
    else:
        components["内向性"] -= 30; trait_keywords.append("Extrovert")

    # Q4: 論理/感情 (T vs F) (変更なし)
    if answers[3] == 'yes':
        components["論理性"] += 40 
        trait_keywords.append("Logical")
    else:
        components["論理性"] -= 30
        components["感受性"] += 40 
        trait_keywords.append("Empathetic")
    
    # --- ▼▼▼ Q5の分析ロジックを修正 ▼▼▼ ---
    # Q5: 説明を受ける時、全体像（なぜ）よりも、具体的な手順（どうやるか）を先に知りたいですか？ (S vs N)
    if answers[4] == 'yes':
        # (「はい」 = 具体的な手順が先 = 感覚型 S)
        components["直感性"] -= 30
        trait_keywords.append("Analytical")
        trait_keywords.append("Present-focused")
    else:
        # (「いいえ」 = 全体像が先 = 直感型 N)
        components["直感性"] += 40
        trait_keywords.append("Intuitive")
        trait_keywords.append("Creative")
        trait_keywords.append("Future-oriented") # 全体像(N)は未来志向と関連
    # --- ▲▲▲ ここまで修正 ▲▲▲ ---

    # Q6: 新規性 (変更なし)
    if answers[5] == 'yes':
        components["直感性"] += 20 
        trait_keywords.append("Spontaneous")
        trait_keywords.append("Creative")
    else:
        components["計画性"] += 20 
        trait_keywords.append("Deliberate")
        trait_keywords.append("Planner")

    # (以降、この関数内の残りのコードは変更なし)
    if avg_time < 0.8:
        trait_keywords.append("Decisive")
    elif avg_time > 2.5:
        trait_keywords.append("Deliberate")

    for key, value in components.items():
        components[key] = max(0, min(100, value))

    all_possible_marks = list(set(trait_keywords) & set(MARK_DEFINITIONS.keys()))
    # ... (マーク選択ロジック) ...
    if len(all_possible_marks) < 2:
        additional_marks = random.sample([m for m in MARK_DEFINITIONS.keys() if m not in all_possible_marks], 2 - len(all_possible_marks))
        selected_marks = all_possible_marks + additional_marks
    else:
        selected_marks = random.sample(all_possible_marks, 2)
        
    if lang == 'en':
        personality_description_for_prompt = ", ".join([MARK_DEFINITIONS[k]["display_name_en"] for k in trait_keywords if k in MARK_DEFINITIONS])
    else:
        personality_description_for_prompt = ", ".join([MARK_DEFINITIONS[k]["display_name"] for k in trait_keywords if k in MARK_DEFINITIONS])
    personality_description_for_image_gen = ", ".join([MARK_DEFINITIONS[k]["display_name_en"] for k in trait_keywords if k in MARK_DEFINITIONS])
    
    return personality_description_for_prompt, personality_description_for_image_gen, components, selected_marks


def generate_ai_content(data):
    # ▼▼▼ 言語設定を取得し、analyze_personality の戻り値を受け取る ▼▼▼
    lang = data.get('lang', 'ja')
    personality_description, personality_for_image, components, selected_marks = analyze_personality(data)
    
    if lang == 'en':
        print(f"Analyzed personality (EN): {personality_description}")
    else:
        print(f"分析された性格 (JP): {personality_description}")
    # ▲▲▲ ここまで ▲▲▲

    # --- メインカラーの決定ロジック (get_main_color) を削除 ★★★ ---
    
    # デフォルト値を設定
    ad_copy_text = "Analysis Error" if lang == 'en' else "分析エラー"
    materials_text = "Analysis Error" if lang == 'en' else "分析エラー"
    precautions_text = "Analysis Error" if lang == 'en' else "分析エラー"
    main_color_theme = "Abstract vibrant colors, dynamic composition" # ★★★ フォールバックカラーを追加 ★★★

    try:
        print("広告コピー、原材料、取り扱い注意、メインカラーをAIで生成中...")
        
        # --- ▼▼▼ システムプロンプトを言語に応じて動的に構築 ▼▼▼ ---
        
        if lang == 'en':
            output_language = "English"
            ad_copy_example = "e.g., 'This bottle is a planned yet passionate blend.' 'Enjoy the emotionally rich and passionate flavor.' Do not use phrases like 'The perfect drink for you...' and do not use quotation marks."
            materials_example = "e.g., 'A dash of planning', 'A pinch of intuition'."
            precautions_example = "e.g., 'Handle with care,' 'May suddenly become passionate.'"
            color_theme_instruction = "a creative main color theme written **in English**."
            
            system_prompt_template = (
                "You are a highly creative copywriter and brand strategist. Analyze the user's personality and generate 4 types of content as if they were a bottled beverage. Generate all text in {language}.\n"
                "1. **Ad Copy**: Create a catchy ad copy in {language} that introduces this 'person' as a beverage to third parties, Within 30 words. {ad_copy_example}\n"
                "2. **Ingredients**: Create a list of 4 metaphorical 'ingredients' that make up the person, in {language}.\n"
                "3. **Handling Precautions**: Create 3 metaphorical handling precautions for interacting with this person, as a bulleted list (using '・') in {language}. {precautions_example}\n" # ★日本の「・」に統一
                "4. **Main Color**: Describe {color_theme_instruction} (e.g., 'Vibrant Pink and Warm Orange tones', 'Deep Blue and Cool Silver tones').\n"
                "- e.g., 'Vibrant Pink and Warm Orange tones', 'Deep Blue and Cool Silver tones', 'Sunny Yellow and Earthy Green'.\n"
                "- **Important**: Ensure a variety of colors, not just purple or blue.\n"
                "\n"
                "Strictly format the output using '---', '###', and '%%%' as separators:\n"
                "Ad Copy: [Ad copy here]\n"
                "---\n"
                "Ingredients: [Ingredient 1], [Ingredient 2], ...\n"
                "###\n"
                "Handling Precautions:\n・[Precaution 1]\n・[Precaution 2]\n" # ★日本の「・」に統一
                "%%%\n"
                "Main Color: [English color theme here]"
            )
            
            system_prompt = system_prompt_template.format(
                language=output_language,
                ad_copy_example=ad_copy_example,
                materials_example=materials_example,
                precautions_example=precautions_example,
                color_theme_instruction=color_theme_instruction
            )
            
        else: # lang == 'ja' (デフォルト)
            system_prompt = (
                "あなたは非常に創造的なコピーライターであり、ブランド戦略家です。ユーザーの性格を分析し、その人物がまるでペットボトル飲料であるかのように見立てて、4種類のコンテンツを生成してください。\n"
                "1. **広告コピー**: その「人物」を飲料に見立てて第三者に紹介・アピールするような、キャッチーな広告コピーを日本語で作成してください。例えば、「この一本は、計画性がありながら情熱的な一本です。」「感情豊かで情熱的な味わいをお楽しみください。」注意してほしいのは、その人物に向けたドリンクではないので、「〜なあなたにぴったりなドリンク」というような言い方はやめてください。また鉤括弧「」などはいりません。\n"
                "2. **原材料**: その人物を構成する比喩的な「原材料」のリストを6つ日本語で作成してください。例えば、単に「計画性」とするのではなく「計画性のスパイス」などとしてください。\n"
                "3. **取り扱い注意**: その人物と接する上での比喩的な注意書きを3個、日本語で箇条書き（・）で作成してください。\n"
                "4. **メインカラー**: その人物の性格を最もよく表す、創造的なメインカラーテーマを**英語で**記述してください。 (例: 'Vibrant Pink and Warm Orange tones', 'Deep Blue and Cool Silver tones')\n"
                "- 例: 'Vibrant Pink and Warm Orange tones', 'Deep Blue and Cool Silver tones', 'Sunny Yellow and Earthy Green'.\n"
                "- **重要**: 紫（purple）系や青（blue）系ばかりにならないようにしてください。一見合わないような奇抜な色の組み合わせでも良いです。\n"
                "\n"
                "出力は厳密に以下の形式で、'---'と'###'と'%%%'を切りとしてください。\n"
                "広告コピー: [ここに広告コピー]\n"
                "---\n"
                "原材料: [材料1], [材料2], ...\n"
                "###\n"
                "取り扱い注意:\n・[注意1]\n・[注意2]\n"
                "%%%\n"
                "メインカラー: [ここに英語のカラーテーマ]"
            )
        # --- ▲▲▲ プロンプト構築ここまで ▲▲▲ ---
        
        # ▼▼▼ ユーザープロンプトには、AIが指定した言語の性格説明を渡す ▼▼▼
        user_prompt = f"User Personality Traits: {personality_description}"
        completion = openai_client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], temperature=0.9)
        response_text = completion.choices[0].message.content
        
        # --- ★★★ パーシング(解析)ロジックを修正 (4項目対応) ★★★ ---
        
        # (パーシングロジックは変更なし)
        parts_color = response_text.split('%%%')
        if len(parts_color) == 2:
            main_color_theme = parts_color[1].replace('メインカラー:', '').replace('Main Color:', '').strip()
            rest_of_text = parts_color[0]
        else:
            rest_of_text = parts_color[0]
        parts_main = rest_of_text.split('###')
        if len(parts_main) == 2:
            precautions_text = parts_main[1].replace('取り扱い注意:', '').replace('Handling Precautions:', '').strip()
            content_part = parts_main[0]
        else:
            content_part = parts_main[0]
        parts_content = content_part.split('---')
        if len(parts_content) == 2:
            ad_copy_text = parts_content[0].replace('広告コピー:', '').replace('Ad Copy:', '').strip()
            materials_text = parts_content[1].replace('原材料:', '').replace('Ingredients:', '').strip()
        else:
             ad_copy_text = parts_content[0].replace('広告コピー:', '').replace('Ad Copy:', '').strip()

        print(f"決定されたメインカラーテーマ (AI生成): {main_color_theme}")

    except Exception as e:
        print(f"テキスト生成でエラーが発生しました: {e}")

    generated_image = None
    
    try:
        print("画像を生成中 (メインカラー指定)...")

        # ▼▼▼ 画像生成プロンプトには「英語固定」の性格説明 (personality_for_image) を使用 ▼▼▼
        image_prompt = (
            f"A unique and innovative abstract graphic background design for a beverage label. "
            f"The design must prominently feature a color palette dominated by {main_color_theme}. "
            f"It should metaphorically represent the personality traits: {personality_for_image}. "
            f"Focus on a dynamic composition and intriguing textures using these colors. "
            f"The design must be flat, 2D, suitable for a printable background. "
            f"Do not include any text, letters, words, or logos. "
            f"Avoid 3D rendering, product shots, or realistic scenes. "
            f"Digital art, high resolution, square aspect ratio."
        )
        # ▲▲▲ ここまで ▲▲▲
        
        negative_prompt = (
            "text, letters, words, writing, logo, bottle, product shot, 3d render, photo, realistic, "
            "human, scene, environment, objects, scenery, realistic lighting, shadow, low quality, blurry, watermark, gradient"
        )
        
        response = imagen_model.generate_images(
            prompt=image_prompt,
            negative_prompt=negative_prompt,
            number_of_images=1,
            aspect_ratio="1:1"
        )
        generated_image = response.images[0]._pil_image
    except Exception as e:
        print(f"画像生成でエラーが発生しました: {e}")

    return {
        "image": generated_image,
        "ad_copy": ad_copy_text,
        "materials": materials_text,
        "components": components,
        "marks": selected_marks,
        "precautions": precautions_text,
        "nickname": data.get("nickname", "WATASHI")
        # lang はここでは返さず、app.py で追加する
    }