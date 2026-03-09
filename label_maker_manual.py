import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import time
from ai_generator_api import MARK_DEFINITIONS

def draw_text_with_wrap(draw, text, position, font, max_width, line_spacing, fill="black", lang="ja"):
    x, y = position
    lines = []
    
    if lang == 'ja':
        text_to_wrap = text.strip().replace(',', '、')
    else:
        text_to_wrap = text.strip() 

    # 英語のワードラップに対応
    if lang == 'en':
        words = text_to_wrap.split(' ')
        current_line = ""
        for word in words:
            # AIが生成した改行（\n）も考慮する (例: 取り扱い注意)
            if '\n' in word:
                sub_words = word.split('\n')
                for i, sub_word in enumerate(sub_words):
                    if i > 0: # 意図的な改行
                        lines.append(current_line.strip())
                        lines.append("\n") # 改行マーカー
                        current_line = sub_word
                    else: # 改行前の部分
                        if not sub_word: continue
                        test_line = (current_line + " " + sub_word).strip()
                        
                        if hasattr(font, 'getlength'):
                            line_width = font.getlength(test_line)
                        else:
                            box = font.getbbox(test_line)
                            line_width = box[2] - box[0]
                        
                        if line_width <= max_width:
                            current_line = test_line
                        else:
                            lines.append(current_line.strip())
                            current_line = sub_word
                continue # 次の 'word' ループへ

            # 通常の単語処理
            test_line = (current_line + " " + word).strip()
            
            if hasattr(font, 'getlength'):
                line_width = font.getlength(test_line)
            else:
                box = font.getbbox(test_line)
                line_width = box[2] - box[0]

            if line_width <= max_width:
                current_line = test_line
            else:
                # 1単語が長すぎて行に入らない場合
                if not current_line and line_width > max_width:
                     lines.append(word) # 強制的に追加
                     current_line = ""
                else:
                    # 通常の改行
                    lines.append(current_line.strip())
                    current_line = word
        lines.append(current_line.strip()) # 最後の行を追加
    
    # 日本語の文字ごと改行 (元のロジック)
    else: # lang == 'ja'
        current_line = ""
        for char in text_to_wrap:
            if char == '\n':
                lines.append(current_line)
                lines.append("\n")
                current_line = ""
                continue
                
            if hasattr(font, 'getlength'):
                line_width = font.getlength(current_line + char)
            else:
                box = font.getbbox(current_line + char)
                line_width = box[2] - box[0]
            
            if line_width <= max_width:
                current_line += char
            else:
                lines.append(current_line)
                current_line = char
        lines.append(current_line)

    # 描画ロジック (共通)
    current_y = y
    for line in lines:
        if line == "\n":
            # 意図的な改行の場合、line_heightではなく固定のspacingだけを追加
            current_y += line_spacing 
            continue
        if not line.strip(): # 空白行はスキップ
            continue
        
        draw.text((x, current_y), line, fill=fill, font=font)
        
        if hasattr(font, 'getbbox'):
            box = font.getbbox(line)
            line_height = box[3] - box[1]
        else:
            line_height = font.getsize(line)[1] # フォールバック
        
        # 描画した行の高さ + 行間
        current_y += line_height + line_spacing 
    return current_y


def create_label(ai_results):
    lang = ai_results.get('lang', 'ja')
    print(f"ラベルを生成中 (言語: {lang})")
    
    scale = 2
    
    final_label_width = 2717
    final_label_height = 768
    
    high_res_width, high_res_height = final_label_width * scale, final_label_height * scale
    
    glue_margin_width = 100 * scale
    effective_width = high_res_width - glue_margin_width
    
    ivory_color = "#ffffff"
    label = Image.new('RGB', (high_res_width, high_res_height), ivory_color)
    draw = ImageDraw.Draw(label)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
        font_body = ImageFont.truetype(font_path, size=32 * scale)
        font_header = ImageFont.truetype(font_path, size=40 * scale)
        print("太字フォント (W6) をロードしました。")
    except Exception as e:
        print(f"太字フォント(W6)の読み込みに失敗: {e}。標準フォント(W4)を試します。")
        try:
            font_path_fallback = "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"
            font_body = ImageFont.truetype(font_path_fallback, size=32 * scale)
            font_header = ImageFont.truetype(font_path_fallback, size=40 * scale)
            print("フォールバックとして W4 フォントをロードしました。")
        except Exception as e2:
            print(f"W4フォントの読み込みにも失敗: {e2}。デフォルトフォントを使用します。")
            font_body = ImageFont.load_default(size=32 * scale)
            font_header = ImageFont.load_default(size=40 * scale)

    font_logo = None
    logo_font_size = 180 * scale
    font_options = [
        "/System/Library/Fonts/Arial Rounded MT Bold.ttf",
        "/System/Library/Fonts/Supplemental/ChalkboardSE-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/ヒラギノ丸ゴシック StdN W8.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    ]
    for f_path in font_options:
        try:
            font_logo = ImageFont.truetype(f_path, size=logo_font_size)
            print(f"ロゴ用フォント '{os.path.basename(f_path)}' をロードしました。")
            break
        except IOError:
            continue
        except Exception as e:
            print(f"ロゴ用フォントのロード中にエラーが発生しました ({f_path}): {e}")
            continue
    if font_logo is None:
        print("指定されたロゴ用フォントが見つからなかったため、デフォルトフォントを使用します。")
        font_logo = ImageFont.load_default(size=logo_font_size)


    # --- パネルの座標定義 ---
    padding = 65 * scale
    front_panel_width = int(high_res_width * 0.45)
    spine_width = int(high_res_width * 0.07)
    back_panel_x_start = front_panel_width + spine_width

    # --- 表紙 (Front Panel) ---
    if ai_results.get("image"):
        bg_image = ImageOps.fit(ai_results["image"], (front_panel_width, high_res_height), Image.Resampling.LANCZOS)
        label.paste(bg_image, (0, 0))

    nickname = ai_results.get("nickname", "WATASHI")
    logo_text_top = nickname.upper() 
    logo_text_bottom = "CIDER"
    def get_text_bbox(text, font):
        if hasattr(font, 'getbbox'):
            return font.getbbox(text)
        else:
            w, h = font.getsize(text)
            return (0, 0, w, h)
    bbox_top = get_text_bbox(logo_text_top, font_logo)
    logo_top_w = bbox_top[2] - bbox_top[0]
    logo_top_h = bbox_top[3] - bbox_top[1]
    logo_top_x = (front_panel_width - logo_top_w) // 2
    logo_top_y = (high_res_height // 2) - logo_top_h - (40 * scale)
    bbox_bottom = get_text_bbox(logo_text_bottom, font_logo)
    logo_bottom_w = bbox_bottom[2] - bbox_bottom[0]
    logo_bottom_x = (front_panel_width - logo_bottom_w) // 2
    logo_bottom_y = (high_res_height // 2) - (15 * scale)
    shadow_color = "black"
    offset = 4 * scale
    draw.text((logo_top_x - offset, logo_top_y - offset), logo_text_top, font=font_logo, fill=shadow_color)
    draw.text((logo_top_x + offset, logo_top_y - offset), logo_text_top, font=font_logo, fill=shadow_color)
    draw.text((logo_top_x - offset, logo_top_y + offset), logo_text_top, font=font_logo, fill=shadow_color)
    draw.text((logo_top_x + offset, logo_top_y + offset), logo_text_top, font=font_logo, fill=shadow_color)
    draw.text((logo_bottom_x - offset, logo_bottom_y - offset), logo_text_bottom, font=font_logo, fill=shadow_color)
    draw.text((logo_bottom_x + offset, logo_bottom_y - offset), logo_text_bottom, font=font_logo, fill=shadow_color)
    draw.text((logo_bottom_x - offset, logo_bottom_y + offset), logo_text_bottom, font=font_logo, fill=shadow_color)
    draw.text((logo_bottom_x + offset, logo_bottom_y + offset), logo_text_bottom, font=font_logo, fill=shadow_color)
    draw.text((logo_top_x, logo_top_y), logo_text_top, font=font_logo, fill="white")
    draw.text((logo_bottom_x, logo_bottom_y), logo_text_bottom, font=font_logo, fill="white")
    
    # --- 背表紙 (Spine) ---
    try:
        barcode_path = os.path.join(base_dir, "assets", "icons", "barcode.png")
        barcode_img = Image.open(barcode_path).convert("RGBA")
        cfi_mark_path = os.path.join(base_dir, "assets", "icons", "cfi_mark.png")
        cfi_mark_img = Image.open(cfi_mark_path).convert("RGBA")
        barcode_rotated = barcode_img.transpose(Image.Transpose.ROTATE_90)
        barcode_w_target = int(spine_width * 0.8) 
        barcode_h_target = int(barcode_w_target / barcode_rotated.width * barcode_rotated.height)
        barcode_resized = barcode_rotated.resize((barcode_w_target, barcode_h_target), Image.Resampling.LANCZOS)
        barcode_pos = (front_panel_width + (spine_width - barcode_w_target)//2, high_res_height - padding - barcode_h_target+70)
        label.paste(barcode_resized, barcode_pos, barcode_resized)
        cfi_h = int(spine_width * 0.8)
        cfi_w = cfi_h
        cfi_resized = cfi_mark_img.resize((cfi_w, cfi_h), Image.Resampling.LANCZOS)
        cfi_pos = (front_panel_width + (spine_width - cfi_w)//2, padding-40)
        label.paste(cfi_resized, cfi_pos, cfi_resized)
    except FileNotFoundError as e:
        print(f"アイコン画像が見つかりません。'assets/icons'フォルダを確認してください: {e}")
    
    
    # --- 裏面 (Back Panel) ---
    mark_size = 170 * scale
    mark_area_width = mark_size + padding
    back_panel_padding = 10 * scale
    mark_x_start = effective_width - padding - mark_size
    if ai_results.get("marks"):
        for i, mark_key in enumerate(ai_results["marks"]):
            mark_info = MARK_DEFINITIONS.get(mark_key)
            if mark_info:
                try:
                    mark_path = os.path.join(base_dir, "assets", "marks", mark_info['file'])
                    mark_img = Image.open(mark_path).convert("RGBA")
                    mark_resized = mark_img.resize((mark_size, mark_size), Image.Resampling.LANCZOS)
                    mark_pos = (mark_x_start, 30 + (mark_size + (5 * scale)) * i)
                    label.paste(mark_resized, mark_pos, mark_resized)
                except FileNotFoundError:
                    print(f"マーク画像が見つかりません: {mark_info['file']}")
    try:
        labelme_mark_path = os.path.join(base_dir, "assets", "icons", "labelme_mark.png") 
        labelme_mark_img = Image.open(labelme_mark_path).convert("RGBA")
        labelme_mark_resized = labelme_mark_img.resize((mark_size, mark_size), Image.Resampling.LANCZOS)
        mark_pos_y = 30 + (mark_size + (5 * scale)) * 2
        mark_pos = (mark_x_start, mark_pos_y)
        label.paste(labelme_mark_resized, mark_pos, labelme_mark_resized)
    except FileNotFoundError:
        print(f"マーク画像が見つかりません: {labelme_mark_path}")
    except Exception as e:
        print(f"labelme_mark.png の読み込み中にエラーが発生しました: {e}")

    # 裏面見出しの多言語対応
    ad_copy_x = back_panel_x_start + back_panel_padding
    ad_copy_max_width = effective_width - ad_copy_x - mark_area_width - back_panel_padding
    
    if lang == 'en':
        header_secret = f"{nickname.upper()}'S CIDER SECRET"
        header_precautions = "Handling Precautions"
        header_components = "Personality Components"
        header_materials = "Ingredients"
    else: # ja
        header_secret = f"{nickname.upper()} CIDERのひみつ"
        header_precautions = "お取り扱い上の注意"
        header_components = "性格成分表示"
        header_materials = "原材料"

    draw.text((ad_copy_x, back_panel_padding+20), header_secret , font=font_header, fill="black")
    ad_copy_end_y = 0
    if ai_results.get("ad_copy"):
        
        ad_copy_end_y = draw_text_with_wrap(
            draw, ai_results["ad_copy"], 
            (ad_copy_x, back_panel_padding + 70*scale), 
            font_body, max_width=ad_copy_max_width, line_spacing=20*scale,
            lang=lang 
        )

    if ai_results.get("precautions") and ad_copy_end_y > 0:
        precautions_start_y = ad_copy_end_y + 20 * scale 
        draw.text((ad_copy_x, precautions_start_y), header_precautions, font=font_header, fill="black")
        
        draw_text_with_wrap(
            draw, ai_results["precautions"],
            (ad_copy_x, precautions_start_y + 70*scale),
            font_body, max_width=ad_copy_max_width, line_spacing=10*scale,
            lang=lang
        )
        
    bottom_section_start_y = int(high_res_height * (5/7))
    
    components_x = back_panel_x_start + back_panel_padding
    draw.text((components_x, bottom_section_start_y), header_components, font=font_header, fill="black")
    
    if ai_results.get("components"):
        component_y_start = bottom_section_start_y + 60 * scale
        
        if lang == 'en':
            # 英語は長いため列幅を広げる
            column_width = 280 * scale
            component_name_map = {
                "内向性": "Introvert",
                "直感性": "Intuition",
                "計画性": "Planning",
                "協調性": "sociability",
                "論理性": "Logic",
                "感受性": "Sensitivity"
            }
        else:
            column_width = 200 * scale # 元の幅
            # 日本語の場合はキーをそのまま使う
            component_name_map = {k: k for k in ai_results.get("components", {}).keys()}
        # ▲▲▲
            
        row_height = 50 * scale
        components_items = list(ai_results["components"].items())
        
        for i, (name_ja, value) in enumerate(components_items):
            
            name_display = component_name_map.get(name_ja, name_ja)
            
            col = i // 3 # 0, 0, 0, 1, 1, 1
            row = i % 3 # 0, 1, 2, 0, 1, 2
            current_x = components_x + (col * column_width)
            current_y = component_y_start + (row * row_height)
            
            line = f"{name_display}: {value}%"
            draw.text((current_x, current_y), line, font=font_body, fill="black")

    materials_x = components_x + (2 * column_width) + (20 * scale) 
    
    draw.text((materials_x, bottom_section_start_y), header_materials, font=font_header, fill="black")
    if ai_results.get("materials"):
        materials_max_width = effective_width - materials_x - padding
        
        if materials_max_width > 0:
            draw_text_with_wrap(draw, ai_results["materials"],
                                (materials_x, bottom_section_start_y + 60*scale),
                                font_body, max_width=materials_max_width, line_spacing=20*scale,
                                lang=lang
            )


    final_label_image = label.resize((final_label_width, final_label_height), Image.Resampling.LANCZOS)
    

    border_width = 5 
    draw_final = ImageDraw.Draw(final_label_image)
    draw_final.rectangle((0, 0, final_label_width - 1, border_width - 1), fill="black")
    draw_final.rectangle((0, 0, border_width - 1, final_label_height - 1), fill="black")
    draw_final.rectangle((0, final_label_height - border_width, final_label_width - 1, final_label_height - 1), fill="black")
    margin_top = 60
    margin_bottom = 156+96
    new_width = final_label_width
    new_height = final_label_height + margin_top + margin_bottom
    final_image_with_margin = Image.new('RGB', (new_width, new_height), "white")
    final_image_with_margin.paste(final_label_image, (0, margin_top))
    timestamp = int(time.time())
    if not os.path.exists("generated_labels"): os.makedirs("generated_labels")
    label_path = os.path.join(base_dir, "generated_labels", f"final_label_{timestamp}.png")
    final_image_with_margin.save(label_path)
    
    return label_path