"""Test integer ID mapping for ranking."""

# Simulate the mapping logic
experiences = [
    {"id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "title": "Senior Engineer"},
    {"id": "b2c3d4e5-f6a7-8901-bcde-f12345678901", "title": "Junior Developer"},
    {"id": "c3d4e5f6-a7b8-9012-cdef-123456789012", "title": "Team Lead"},
]

# Create mappings
exp_id_to_int = {}
int_to_exp_id = {}
for idx, exp in enumerate(experiences, start=1):
    exp_uuid = exp["id"]
    exp_id_to_int[exp_uuid] = idx
    int_to_exp_id[idx] = exp_uuid

print("=== Integer to UUID Mapping ===")
print(f"Mapping: {int_to_exp_id}")
print()

# Simulate LLM sending integers
llm_response = {
    "ranked_experience_ids": [3, 1, 2]  # LLM ranks: Team Lead, Senior Engineer, Junior Developer
}

print("=== LLM Response ===")
print(f"LLM returned: {llm_response['ranked_experience_ids']}")
print()

# Map back to UUIDs
ranked_exp_uuids = []
for int_id in llm_response["ranked_experience_ids"]:
    if int_id in int_to_exp_id:
        ranked_exp_uuids.append(int_to_exp_id[int_id])
        print(f"Integer {int_id} -> UUID {int_to_exp_id[int_id]}")

print()
print("=== Final Ranked UUIDs ===")
print(ranked_exp_uuids)
print()

# Verify we can find them in original data
exp_dict = {exp["id"]: exp for exp in experiences}
print("=== Verification ===")
for uuid in ranked_exp_uuids:
    if uuid in exp_dict:
        print(f"✓ Found: {exp_dict[uuid]['title']}")
    else:
        print(f"✗ Missing: {uuid}")
