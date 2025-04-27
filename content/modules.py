MODULES = {
    1: {
        'id': 1,
        'title': '📚 Глава 1: Введение в сетевой анализ',
        'description': 'Основные концепции и инструменты сетевого анализа',
        'submodules': {
            1: {
                'id': 1,
                'title': '1.1. Что такое сетевой анализ?',
                'pages': 3,
                'description': 'Определение и основные задачи'
            },
            2: {
                'id': 2,
                'title': '1.2. Зачем нужен сетевой анализ?',
                'pages': 3,
                'description': 'Практическое применение и преимущества'
            },
            3: {
                'id': 3,
                'title': '1.3. Как работает сетевой анализ?',
                'pages': 3,
                'description': 'Процесс захвата и анализа пакетов'
            },
            4: {
                'id': 4,
                'title': '1.4. Применение в различных сферах',
                'pages': 2,
                'description': 'Использование в безопасности, администрировании и разработке'
            },
            5: {
                'id': 5,
                'title': '1.5. Основные инструменты',
                'pages': 3,
                'description': 'Wireshark, Tcpdump, Nmap и другие'
            }
        }
    },
    2: {
        'id': 2,
        'title': '🔌 Глава 2: Сетевые протоколы',
        'description': 'Изучение основных сетевых протоколов',
        'submodules': {
            1: {
                'id': 1,
                'title': '2.1. Протоколы TCP/IP',
                'pages': 4,
                'description': 'Основы стека протоколов TCP/IP'
            },
            2: {
                'id': 2,
                'title': '2.2. HTTP и HTTPS',
                'pages': 3,
                'description': 'Анализ веб-трафика'
            },
            3: {
                'id': 3,
                'title': '2.3. DNS и DHCP',
                'pages': 2,
                'description': 'Протоколы разрешения имен'
            },
            4: {
                'id': 4,
                'title': '2.4. Беспроводные протоколы',
                'pages': 3,
                'description': 'Wi-Fi, Bluetooth и другие'
            }
        }
    },
    3: {
        'id': 3,
        'title': '🛡️ Глава 3: Безопасность',
        'description': 'Анализ сетевых угроз и защита',
        'submodules': {
            1: {
                'id': 1,
                'title': '3.1. Обнаружение атак',
                'pages': 3,
                'description': 'DDoS, MITM, сканирование портов'
            },
            2: {
                'id': 2,
                'title': '3.2. Анализ вредоносного трафика',
                'pages': 2,
                'description': 'Выявление подозрительной активности'
            },
            3: {
                'id': 3,
                'title': '3.3. VPN и шифрование',
                'pages': 3,
                'description': 'Анализ зашифрованного трафика'
            }
        }
    },
    4: {
        'id': 4,
        'title': '🔍 Глава 4: Диагностика сети',
        'description': 'Методы поиска и устранения проблем',
        'submodules': {
            1: {
                'id': 1,
                'title': '4.1. Анализ производительности',
                'pages': 3,
                'description': 'Выявление узких мест'
            },
            2: {
                'id': 2,
                'title': '4.2. Диагностика соединений',
                'pages': 2,
                'description': 'TCP-анализ, потеря пакетов'
            },
            3: {
                'id': 3,
                'title': '4.3. Оптимизация трафика',
                'pages': 3,
                'description': 'Методы улучшения работы сети'
            }
        }
    },
    5: {
        'id': 5,
        'title': '⚡ Глава 5: Продвинутые техники',
        'description': 'Экспертные методы анализа',
        'submodules': {
            1: {
                'id': 1,
                'title': '5.1. Анализ VoIP трафика',
                'pages': 3,
                'description': 'Диагностика качества голосовой связи'
            },
            2: {
                'id': 2,
                'title': '5.2. IoT устройства',
                'pages': 2,
                'description': 'Анализ трафика умных устройств'
            },
            3: {
                'id': 3,
                'title': '5.3. Автоматизация анализа',
                'pages': 3,
                'description': 'Скрипты и инструменты автоматизации'
            },
            4: {
                'id': 4,
                'title': '5.4. Отчетность',
                'pages': 2,
                'description': 'Создание профессиональных отчетов'
            }
        }
    }
}

def get_module(module_id: int) -> dict:
    """Получает данные модуля по ID"""
    return MODULES.get(module_id, {})

def get_submodule(module_id: int, submodule_id: int) -> dict:
    """Получает данные подмодуля по ID модуля и подмодуля"""
    module = get_module(module_id)
    return module.get('submodules', {}).get(submodule_id, {})

def get_total_modules() -> int:
    """Возвращает общее количество доступных модулей"""
    return len(MODULES)

def get_total_submodules(module_id: int) -> int:
    """Возвращает количество подмодулей в указанном модуле"""
    module = get_module(module_id)
    return len(module.get('submodules', {}))