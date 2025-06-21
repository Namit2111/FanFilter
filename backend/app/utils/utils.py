def load_txt_file(file_name):
    with open(f"app/prompts/{file_name}", 'r') as file:
        return file.read()
