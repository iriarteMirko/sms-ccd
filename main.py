from src.models.app_sms import App_SMS
import warnings


def main() -> None:
    warnings.filterwarnings("ignore")
    app: App_SMS = App_SMS()
    app.crear_app()


if __name__ == "__main__":
    main()