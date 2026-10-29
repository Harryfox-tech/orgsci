# 已补全文：Acemoglu—Pischke（2000）

2026-10-28。用户先提供ScienceDirect多篇压缩包，随后明确指定桌面的 `1-s2.0-S0014292199000495-main.pdf` 为全文；以后一份为准。

## 阅读入口

- [完整精读与方案一对照](01_Acemoglu_Pischke_2000_全文精读与模型对照.md)
- [关键主张与印刷页码台账](02_关键主张与页码台账.md)
- `source_manifest.json`：文件身份、哈希、页数与原始路径。
- `review_evidence.json`：实际全文/视觉核验范围及计算不变性。

**当前判断**：该文没有直接建立私人诊断—L/V选择—独立验证名额的全部机制，但已经研究认证改变培训投入，并在p.926讨论能力替代努力取得证书。因此，不再需要用户补这篇全文，也不能以“认证让人少学习”宣称新空白。最小模型结果保留为“新增岗位达标比例”的条件推论，独立理论贡献仍待检验。

## 来源与复核

[正式DOI](https://doi.org/10.1016/S0014-2921(99)00049-5)，European Economic Review 44(4–6):917–927，11页。已读取全部文字，关键页以渲染图复核，未把损坏字体的抽取结果当作数学式。

复做本机提取/渲染：

```powershell
python -X utf8 00_project_management/minimal_diagnosis_2026_10_28/fulltext_review/inspect_supplied_pdf.py --pdf "C:/Users/shiqing peng/Desktop/1-s2.0-S0014292199000495-main.pdf" --render
```

需要pypdf及Poppler；本机使用bundled运行时。依据仓库既有全文处理约定，原文不额外公开复制，文字与页图留在被忽略的 `local_cache/`。当前没有扩展ZIP中其他论文、新增检索、修改模型或推送。
