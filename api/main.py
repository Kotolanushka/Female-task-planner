@app.post("/advice", response_model=AdviceOut)
def advice(payload: AdviceIn):
    ctx = docs_to_context(retriever.get_relevant_documents(payload.task))
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role":"system","content":pick_system(payload.locale)},
            {"role":"user","content":build_user_prompt(payload.phase, payload.task, payload.locale, ctx)}
        ],
        response_format={"type":"json_object"},
        temperature=0.2
    )
    raw = resp.choices[0].message.content
    try:
        obj = json.loads(raw)
        v = obj.get("verdict","ok")
        if v not in ("good","ok","avoid"): v="ok"
        return AdviceOut(verdict=v, reason=obj.get("reason",""), suggestion=obj.get("suggestion",""))
    except Exception:
        fallback = {
            "menstruation": ("avoid","низкая энергия","перенеси или упростить"),
            "follicular":   ("good","хорошее время для старта","запланируй первые шаги"),
            "ovulation":    ("good","пик коммуникаций","назначь встречи/презентации"),
            "luteal":       ("ok","фокус и завершение","разбей на подзадачи"),
            "unknown":      ("ok","недостаточно данных","ориентируйся на самочувствие"),
        }
        v,r,s = fallback.get(payload.phase, fallback["unknown"])
        return AdviceOut(verdict=v, reason=r, suggestion=s)

@app.get("/health")
def health(): return {"ok": True}