def get_learning_recommendations(topic: str, level: str = "beginner") -> list[str]:
    base = [
        f"Learn the basic definition of {topic}.",
        f"Study one real-world example of {topic}.",
        f"Practice 5 short questions about {topic}.",
        f"Review the topic and write a summary in your own words.",
    ]

    if level.lower() == "advanced":
        return [
            f"Analyze complex cases related to {topic}.",
            f"Compare {topic} with a similar concept.",
            f"Build a small project or challenge around {topic}.",
            f"Explain {topic} to someone else using examples.",
        ]

    return base
