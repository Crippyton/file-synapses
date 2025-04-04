import shutil
import os

def zipar_pasta(txt_pasta, page):
    if not txt_pasta.value:
        return
    zip_path = shutil.make_archive(os.path.join(txt_pasta.value, "estrutura_compactada"), 'zip', txt_pasta.value)
    page.snack_bar = ft.SnackBar(ft.Text(f"ZIP criado: {zip_path} ✅"), open=True)
    page.update()
