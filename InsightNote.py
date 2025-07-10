import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import datetime
import csv

DATA_FILE = "insights.json"

class InsightNoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InsightNote")

        self.insights = self.load_data()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.build_add_tab()
        self.build_search_tab()
        self.build_export_tab()
        self.build_help_tab()

    def build_add_tab(self):
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Add Insight")

        ttk.Label(self.add_tab, text="Insight Type:").grid(row=0, column=0, sticky="w")
        self.insight_type = ttk.Combobox(self.add_tab, values=["Command", "Concept", "Mistake", "Quote", "Contact", "Idea", "Fix"], state="readonly")
        self.insight_type.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.add_tab, text="Title:").grid(row=1, column=0, sticky="w")
        self.title_entry = ttk.Entry(self.add_tab, width=50)
        self.title_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.add_tab, text="Details:").grid(row=2, column=0, sticky="nw")
        self.details_text = tk.Text(self.add_tab, width=60, height=10)
        self.details_text.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.add_tab, text="Tags (comma separated):").grid(row=3, column=0, sticky="w")
        self.tags_entry = ttk.Entry(self.add_tab, width=50)
        self.tags_entry.grid(row=3, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(self.add_tab, text="Save Insight", command=self.save_insight)
        self.add_button.grid(row=4, column=1, sticky="e", pady=10)

    def build_search_tab(self):
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Search & View")

        ttk.Label(self.search_tab, text="Search:").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(self.search_tab, width=50)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(self.search_tab, text="Search", command=self.search_insights)
        self.search_button.grid(row=0, column=2, padx=5)

        self.result_list = tk.Listbox(self.search_tab, width=120, height=15)
        self.result_list.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.result_list.bind("<<ListboxSelect>>", self.show_details)

        self.delete_button = ttk.Button(self.search_tab, text="Delete Selected", command=self.delete_selected)
        self.delete_button.grid(row=2, column=1, pady=5)

        self.details_label = tk.Label(self.search_tab, text="Details:", font=("Arial", 10, "bold"))
        self.details_label.grid(row=3, column=0, sticky="nw", padx=10)

        self.details_display = tk.Text(self.search_tab, width=90, height=10, wrap="word")
        self.details_display.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

        self.refresh_results()

    def build_export_tab(self):
        self.export_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.export_tab, text="Export")

        ttk.Label(self.export_tab, text="Export insights as:").pack(pady=10)

        ttk.Button(self.export_tab, text="Export to CSV", command=self.export_csv).pack(pady=5)
        ttk.Button(self.export_tab, text="Export to TXT", command=self.export_txt).pack(pady=5)
        ttk.Button(self.export_tab, text="Export to Markdown", command=self.export_md).pack(pady=5)

    def build_help_tab(self):
        self.help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.help_tab, text="How to Use")

        instructions = (
            "🔹 Add Insight Tab:\n"
            "- Choose a type (Command, Idea, Mistake, etc)\n"
            "- Write a short title & detailed description\n"
            "- Add tags like 'Git', 'Network', etc\n\n"
            "🔹 Search & View Tab:\n"
            "- View all insights or search by keyword/tag/type/title\n"
            "- Click to view details\n"
            "- Delete selected if needed\n\n"
            "🔹 Export Tab:\n"
            "- Save all notes to your system in CSV/TXT/MD\n\n"
            "🎯 Tip: Use this tool daily to capture insights while working!\n"
        )

        tk.Message(self.help_tab, text=instructions, width=700, font=("Arial", 11)).pack(padx=10, pady=10)

    def save_insight(self):
        entry = {
            "type": self.insight_type.get(),
            "title": self.title_entry.get(),
            "details": self.details_text.get("1.0", "end").strip(),
            "tags": self.tags_entry.get(),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if not entry["type"] or not entry["title"]:
            messagebox.showerror("Missing Fields", "Please fill in all fields.")
            return

        self.insights.append(entry)
        self.save_data()
        messagebox.showinfo("Saved", "Insight saved successfully!")
        self.clear_form()
        self.refresh_results()

    def search_insights(self):
        query = self.search_entry.get().lower()
        self.result_list.delete(0, "end")
        self.filtered = []

        for ins in self.insights:
            if any(query in str(ins[key]).lower() for key in ["type", "title", "details", "tags"]):
                display = f"{ins['timestamp']} | [{ins['type']}] {ins['title']} - {ins['tags']}"
                self.result_list.insert("end", display)
                self.filtered.append(ins)

        self.details_display.delete("1.0", "end")

    def refresh_results(self):
        self.result_list.delete(0, "end")
        self.filtered = self.insights
        for ins in self.insights:
            display = f"{ins['timestamp']} | [{ins['type']}] {ins['title']} - {ins['tags']}"
            self.result_list.insert("end", display)

    def show_details(self, event):
        index = self.result_list.curselection()
        if not index:
            return
        ins = self.filtered[index[0]]
        self.details_display.delete("1.0", "end")
        self.details_display.insert("end", f"{ins['details']}")

    def delete_selected(self):
        index = self.result_list.curselection()
        if not index:
            messagebox.showerror("No selection", "Please select an item to delete.")
            return
        selected_time = self.filtered[index[0]]["timestamp"]
        self.insights = [i for i in self.insights if i["timestamp"] != selected_time]
        self.save_data()
        self.refresh_results()
        self.details_display.delete("1.0", "end")
        messagebox.showinfo("Deleted", "Insight deleted.")

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "type", "title", "details", "tags"])
            writer.writeheader()
            writer.writerows(self.insights)
        messagebox.showinfo("Exported", "Exported as CSV.")

    def export_txt(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
        if not path:
            return
        with open(path, "w") as f:
            for i in self.insights:
                f.write(f"{i['timestamp']} | {i['type']} | {i['title']}\n{i['details']}\nTags: {i['tags']}\n\n")
        messagebox.showinfo("Exported", "Exported as TXT.")

    def export_md(self):
        path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown File", "*.md")])
        if not path:
            return
        with open(path, "w") as f:
            for i in self.insights:
                f.write(f"### {i['title']} ({i['type']})\n")
                f.write(f"**Timestamp:** {i['timestamp']}\n\n")
                f.write(f"{i['details']}\n\n")
                f.write(f"**Tags:** {i['tags']}\n\n---\n\n")
        messagebox.showinfo("Exported", "Exported as Markdown.")

    def clear_form(self):
        self.insight_type.set("")
        self.title_entry.delete(0, "end")
        self.details_text.delete("1.0", "end")
        self.tags_entry.delete(0, "end")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.insights, f, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = InsightNoteApp(root)
    root.mainloop()
