from agent.supervisor import AgentSupervisor
import json


def print_welcome():
    print("=" * 70)
    print("Agentic Enterprise Assistant – HCLTech Annual Report")
    print("Offline Demo | RAG + Agent + Structured Actions")
    print("Type 'exit' or 'quit' to stop")
    print("=" * 70)


def main():
    agent = AgentSupervisor()
    print_welcome()

    while True:
        try:
            user_input = input("\n> Ask a question:\n").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("\nExiting assistant. Goodbye!")
                break

            if not user_input:
                print("Please enter a valid question.")
                continue

            response = agent.handle(user_input)

            print("\n--- Response ---")

            # -------------------------------
            # ACTION RESPONSE
            # -------------------------------
            if isinstance(response, dict) and "action" in response:
                print("Action Output:")
                print(json.dumps(response, indent=2))

            # -------------------------------
            # INFORMATION RESPONSE
            # -------------------------------
            elif isinstance(response, dict) and "answer" in response:
                print("Answer:")
                print(response["answer"])

            # -------------------------------
            # FALLBACK (SHOULD NOT HAPPEN)
            # -------------------------------
            else:
                print("Unexpected response format:")
                print(response)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting assistant.")
            break

        except Exception as e:
            print("\nAn error occurred:")
            print(str(e))


if __name__ == "__main__":
    main()
