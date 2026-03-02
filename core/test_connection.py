from database import get_supabase_client

def test_connection():
    client = get_supabase_client()
    response = client.table("tickets").select("*").limit(1).execute()
    print("Connection successful. Response:", response)

if __name__ == "__main__":
    test_connection()