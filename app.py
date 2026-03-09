from flask import Flask, render_template, request, jsonify, send_file
import ai_generator_api
import label_maker_manual

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        user_data = request.get_json()
        print("ブラウザからデータを受信:", user_data)
        
        # generate_ai_content は user_data (lang を含む) を受け取る
        ai_results = ai_generator_api.generate_ai_content(user_data)
        
        if not ai_results.get("image") or not ai_results.get("ad_copy"):
            raise Exception("AIコンテンツの生成に失敗しました。")

        # ▼▼▼ ai_results に 'lang' を追加して label_maker に渡す ▼▼▼
        ai_results['lang'] = user_data.get('lang', 'ja')
        
        # 辞書をそのまま渡す
        image_path = label_maker_manual.create_label(ai_results)
        # ▲▲▲ ここまで ▲▲▲
        
        return send_file(image_path, mimetype='image/png')

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        # スタックトレースをターミナルに出力
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)