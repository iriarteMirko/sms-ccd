from src.models.app_sms import App_SMS


def main():
    import warnings
    warnings.filterwarnings("ignore")
    app = App_SMS()
    app.crear_app()


if __name__ == "__main__":
    main()