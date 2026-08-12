from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


LIKERT_ORDER = [
	"Strongly Agree",
	"Agree",
	"Neutral",
	"Disagree",
	"Strongly Disagree",
]

LIKERT_COLORS = {
	"Strongly Agree": "#1A9850",
	"Agree": "#91CF60",
	"Neutral": "#D9D9D9",
	"Disagree": "#FC8D59",
	"Strongly Disagree": "#D73027",
}


def get_question_group(column_name: str) -> str:
	if " [" in column_name:
		group_name = column_name.split(" [", 1)[0]
		return "Engagement" if group_name == "Engagement Appeal" else group_name
	return column_name


def format_question_label(column_name: str) -> str:
	if " [" in column_name and column_name.endswith("]"):
		label = column_name.split(" [", 1)[1][:-1]
	else:
		label = column_name
	if label.startswith("(") and ")" in label:
		start = label.find("(")
		end = label.find(")", start)
		if end != -1:
			italic_part = label[start + 1:end]
			italic_part = italic_part.replace(" ", "\\ ")
			prefix = label[:start].rstrip()
			suffix = label[end + 1:].lstrip()
			label = f"{prefix} ($\\mathit{{{italic_part}}}$) {suffix}".strip()
	return label


def main() -> None:
	csv_path = Path(__file__).resolve().parent / "Raw_Sources" / "PreliminarySurvey.csv"
	df = pd.read_csv(csv_path)

	if df.empty:
		raise ValueError(f"No data found in {csv_path}")

	plot_cols = list(df.columns[1:-2])
	if not plot_cols:
		raise ValueError("No survey question columns found to plot.")

	grouped_cols = {}
	for col in plot_cols:
		grouped_cols.setdefault(get_question_group(col), []).append(col)
	group_order = list(grouped_cols.keys())

	total_rows = sum(len(cols) + 1 for cols in grouped_cols.values())
	fig_height = max(4.2, total_rows * 0.33)
	fig = plt.figure(figsize=(14, fig_height))
	outer = fig.add_gridspec(total_rows, 2, width_ratios=[1.75, 2.45], hspace=0.045, wspace=0.05)

	current_row = 0
	for group_idx, group_name in enumerate(group_order):
		cols_in_group = grouped_cols[group_name]
		title_ax = fig.add_subplot(outer[current_row, :])
		title_ax.axis("off")
		title_ax.text(0.0, 0.5, group_name, fontsize=10, fontweight="bold", ha="left", va="center")
		current_row += 1

		for local_idx, col in enumerate(cols_in_group):
			label_ax = fig.add_subplot(outer[current_row, 0])
			plot_ax = fig.add_subplot(outer[current_row, 1])
			current_row += 1

			label_ax.axis("off")
			label_ax.text(0.0, 0.5, format_question_label(col), fontsize=7.5, ha="left", va="center", wrap=True)

			responses = (
				df[col]
				.astype(str)
				.str.strip()
				.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
				.dropna()
			)
			counts = responses.value_counts().reindex(LIKERT_ORDER, fill_value=0)
			left = 0
			for label in LIKERT_ORDER:
				value = int(counts[label])
				if value == 0:
					continue
				plot_ax.barh([0], [value], left=left, color=LIKERT_COLORS[label], edgecolor="white")
				left += value

			plot_ax.set_yticks([])
			if current_row < total_rows:
				plot_ax.set_xticks([])
			else:
				plot_ax.tick_params(axis="x", labelsize=8, pad=1)
				plot_ax.set_xlabel("Responses", fontsize=8, labelpad=1)
			plot_ax.set_xlim(0, max(1, len(responses) * 1.05))
			for spine in plot_ax.spines.values():
				spine.set_visible(False)

	legend_handles = [
		plt.Line2D([0], [0], color=LIKERT_COLORS[label], lw=8, label=label)
		for label in LIKERT_ORDER
	]
	fig.legend(handles=legend_handles, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, 0.002), fontsize=8)
	fig.subplots_adjust(bottom=0.11, top=0.985)
	output_path = Path(__file__).resolve().parent / "Final_Figures" / "f09.png"
	fig.savefig(output_path, dpi=600, bbox_inches="tight", facecolor="white")
	plt.show()


if __name__ == "__main__":
	main()
