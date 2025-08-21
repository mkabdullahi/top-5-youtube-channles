def generate_dummy_data(category):
    return [
        {
            "name": f"{category} Channel {i+1}",
            "thumbnail": f"https://dummyimage.com/120x90/000/fff&text={category}+{i+1}",
            "subscribers": f"{((i+1)*0.2):.1f}M",
            "recent_video": f"Latest {category} Video {i+1}"
        } for i in range(5)
    ]
