# CleanFrame
Remove metadata (EXIF, GPS, XMP) de imagens sem alterar os pixels.

## Porquê
Sempre que partilho fotos de viagens ou de trabalho, o EXIF vai junto com localização, modelo da câmara, software usado, etc. Não quero que isso acompanhe o ficheiro.   

## Uso
```bash
pip install Pillow
python cleanframe.py
```

Abre a janela, seleccionas ficheiros ou uma pasta, escolhes onde guardar, clica em ⚡ Processar.

## Formatos
JPG, JPEG, PNG, WebP, BMP, TIFF, SVG

## Notas
- O ficheiro de saída ganha o sufixo `_clean` (ex: `foto_clean.jpg`)
- Perda visual impercetível — o objetivo é remover metadados, não re-comprimir
- SVG é tratado como texto (remove comentários, tags de metadata, atributos XMP)
- Imagens muito pequenas (< 50KB) podem sair 1-2KB maiores, é normal

## Requisitos
Python 3.10+
 
Pillow
