        """Minimal CogVideoX example: create one prediction and print the output URL(s)."""
        import cogvideox_api

        output = cogvideox_api.run({
    "prompt": "A woman is talking",
    "input_image": "https://example.com/input.png"
})
        print(output)
