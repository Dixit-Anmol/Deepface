# from deepface import DeepFace

# result = DeepFace.analyze(
#     img_path="C:\\Users\\ASUS\\Desktop\\DeepFace\\ronaldo1.png",
#     actions=["emotion","age", "gender", "race"]
# )

# print(result)

# from deepface import DeepFace

# result = DeepFace.verify(
#     img1_path="C:\\Users\\ASUS\\Desktop\\DeepFace\\ronaldo1.png",
#     img2_path="C:\\Users\\ASUS\\Desktop\\DeepFace\\ronaldo2.png"
# )

# print(result)

# from deepface import DeepFace

# result = DeepFace.find(
#     img_path="E:\\IMP Docs\\IMG_20230521_221901_364-removebg-preview.png",
#     db_path="images",
#     detector_backend="Facenet"
# )

# print(result)

from deepface import DeepFace

DeepFace.stream(
    db_path="images",
    detector_backend="opencv",
    model_name="VGG-Face"
)