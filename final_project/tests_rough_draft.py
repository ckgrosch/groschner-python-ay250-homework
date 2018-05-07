def test_label_reader(txt_file,image_file_1024):
    labels, images = label_reader(txt_file,image_file)
    assert len(labels) == len(images)
