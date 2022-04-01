from .. import loader, utils
import requests
from PIL import Image
import io
from io import BytesIO

def register(cb):
    cb(KodikMod())
class KodikMod(loader.Module):
    strings = {'name': 'KodikApi'}
    async def kodikcmd(self, event):
        types = {'help': 9999, 'year': 1, 'studio': 2, 'status': 3, 'producers': 4, 'genres': 5, 'rand': 6, 'title': 7, 'getfullinfo': 8}
        type = 6
        args = utils.get_args_raw(event)
        s = ''
        n = 0
        info = ''
        limit = None
        try:
            if "аниме" in args or "аниме-фильмы"  in args or "аниме-фильм" in args or "фильмы" in args or "сериалы" in args or "мультфильмы" in args or "мультсериалы" in args or "фильм" in args or "сериал" in args or "мультфильм" in args or "мультсериал" in args:
                if "аниме" in args:
                    kind = 'anime-serial'
                    k = 1
                if "аниме-фильмы" in args or "аниме-фильм":
                    kind = 'аниме'
                    k = 2
                elif "мультфильмы" in args or "мультфильм" in args:
                    kind = 'russian-cartoon,foreign-cartoon,soviet-cartoon'
                    k = 3
                elif "мультсериалы" in args or "мультсериал" in args:
                    kind = 'cartoon-serial'
                    k = 4
                elif "сериалы" in args or "сериал" in args:
                    kind = 'foreign-serial,documentary-serial'
                    k = 5
                elif "фильмы" in args or "фильм" in args:
                    kind = 'foreign-movie,multi-part-film,russian-movie'
                    k = 6
                args = args.split(' ', 1)[1]
            else:
                kind = 'anime,anime-serial'
                k = 1
            if args.split()[0] in types:
                type = types[args.split(" ")[0]]
                if " " in args:
                    args = args.split(' ', 1)[1]
                else:
                    args = None
            if args:
                if "/" in args:
                    limit = args.split('/')[0]
                    args = args.split('/', 1)[1]
                else:
                    limit = 10
            if type == 9999:
                if not args:
                    return await event.edit("<b>Доступные команды помощи:</b> <code>.kodik help</code> <b><</b><code>year</code><b>,</b> <code>studio</code><b>,</b> <code>status</code><b>,</b> <code>producers</code><b>,</b> <code>genres</code><b>,</b> <code>rand</code><b>,</b> <code>title</code><b>,</b> <code>getfullinfo</code><b>,</b> <code>allstudies</code><b>,</b> <code>allproducers</code><b>,</b> <code>allgenres</code><b>>.</b>\n\n"
                                            "<b>Доступные команды:</b> <code>.kodik</code> <b><</b><code>year</code><b>,</b> <code>studio</code><b>,</b> <code>status</code><b>,</b> <code>producers</code><b>,</b> <code>genres</code><b>,</b> <code>rand</code><b>,</b> <code>title</code><b>,</b> <code>getfullinfo</code><b>>.</b>\n\n"
                                            "<b>Аргументы передавать надо через пробел.<b>\n"
                                            "<b>Чтобы указать кол-во выводимых тайтлов нужно поставить перед аргументом / и за ним прописать нужное вам кол-во в int</b> <code>/</code><b>.</b>\n\n"
                                            "<b>Пример:</b> <code>.kodik аниме genres 30/яой</code><b>.</b>\n\n"
                                            "<b>Примечание: В этом API нет видео ресурсов с США, России и СНГ.</b>")
                elif args == "year":
                    return await event.edit("<b>Отправляет список тайтлов, которые были выпущены в указанном году.</b>\n"
                                            "<b>Использование:</b> <code>.kodik</code> <b><тип></b> <code>year</code> <b><кол-во тайтлов:int></b><code>/1995</code><b>.</b>\n\n"
                                            "<b>Пример:</b> <code>.kodik rand year 15/1995</code><b>.</b>")
                elif args == "studio":
                    return await event.edit("<b>Отправляет список тайтлов от указанной студии.\n"
                                            "<b>Использование:</b> <code>.kodik</code> <b><тип></b> <code>studio</code> <b><кол-во тайтлов:int></b><code><название студии></code><b>.</b>\n\n"
                                            "<b>Пример:</b> <code>.kodik status studio 10/J.C.Staff</code><b>.</b>\n"
                                            "<b>Список студий:</b> <code>.kodik help allstudies</code><b>.</b>")
                elif args == "producers":
                    return await event.edit("<b>Отправляет список тайтлов от указанного продюсера.</b>\n"
                                            "<b>Использование</b> <code>.kodik</code> <b><тип></b> <code>studio</code> <b><кол-во тайтлов:int></b><code><продюсер></code><b>.</b>\n\n"
                                            "<b>Пример:<b> <code>.kodik year studio 8/Киси Сэйдзи</b>\n"
                                            "<b>Список продюсеров:</b> <code>.kodik help allproducers</code><b>.</b>")
                elif args == "status":
                    return await event.edit("<b>Отправляет список тайтлов по указанному</b>\n"
                                            "<b>Использование:</b> <code>.kodik</code> <b><тип></b> <code>status</code> <b><кол-во тайтлов:int></b><code><статус></code><b>.</b>\n\n"
                                            "<b>Пример:</b> <code>.kodik studio status 25/ongoing</code><b>.</b>\n"
                                            "<b>Список статусов:</b> <code>anons</code><b>,</b> <code>ongoing</code><b>,</b> <code>released</code><b>,</b> <code>ongoing</code><b>.</b>")
                elif args == "genres":
                    return await event.edit("<b>Отправляет список тайтлов по указанному жанру.</b>\n"
                                            "<b>Использование</b> <code>.kodik</code> <b><тип></b> <code>genres</code> <b><кол-во тайтлов:int></b><code><жанр></code><b>.</b>\n\n"
                                            "<b>Пример:</b> <code>.kodik title genres 18/психология</code><b>.</b>\n"
                                            "<b>Список жанров:</b> <code.kodik help allgenres</code><b>.</b>")
                elif args == "rand":
                    return await event.edit("<b>Просто отправляет список тайтлов (не ебу по каким критериям определяет их расположение).</b>\n"
                                            "<b>Использование:</b> <code>.kodik rand</code><b>.</b>")
                elif args == "getfullinfo":
                    return await event.edit("<b>Отправляет полную информацию по <u>точному названию</u>, чтобы определить <u>точное</u> название тайтла, можно использовать <code>.kodik</code> <b><тип></b> <code>title</code> <b><название>.</b>\n"
                                            "<b>Использование:</b> <code>.kodik</code> <b><тип></b> <code>getfullinfo</code> <b><<u>точное</u> название>.</b>\n\n"
                                            "<b>Пример:</b> <code>.kodik status getfullinfo дворянство</code><b>.</b>")
                elif args == "allstudies":
                    return await event.edit("<b>Пока недоступно.</b>")
                elif args == "allproducers":
                    return await event.edit("<b>Пока недоступно.</b>")
                elif args == "allgenres":
                    data = {'genres_type': 'shikimori'}
                    r = requests.post('https://kodikapi.com/genres?token=8ebf915587af48d001d33127ae55dcb3&types=anime-serial', data=data).json()
                    for i in r["results"]:
                        n += 1
                        s += f'<b>{n})</b> {i["title"]}\n'
                        info = ''.join(s)
                    await event.edit("<b>Все доступные жанры:</b>\n\n" + info)
                    return
                else:
                    return await event.edit("<b>Такого параметра для функции хелп нет.</b>")
            if k == 1:
                qw = "аниме сериалов"
                qws = "аниме сериалу"
            elif k == 2:
                qw = "аниме фильмов"
                qws = "аниме фильму"
            elif k == 3:
                qw = "мультфильмов"
                qws = "мультфильму"
            elif k == 4:
                qw = "мультсериалов"
                qws = "мультсериалу"
            elif k == 5:
                qw = "сериалов"
                qws = "сериалу"
            elif k == 6:
                qw = "фильмов"
                qws = "фильму"
            else:
                qw = "тайтлов"
                qws = "тайтлу"
            if type == 6:
                data = {'limit': limit, 'with_page_links': 'true', 'types': kind}
                answer = f"<b>Сборка рандомных тайтлов:</b>"
            if type == 5:
                data = {'limit': limit,'with_page_links': 'true', 'anime_genres': args, 'types': kind}
                answer = f"<b>Сборка \"{qw}\" по жанру(ам) \"{args}\":</b>"
            if type == 4:
                data = {'limit': limit,'with_page_links': 'true', 'producers': args, 'types': kind}
                answer = f"<b>Сборка \"{qw}\" от продюсера \"{args}\":</b>"
            if type == 3:
                data = {'limit': limit,'with_page_links': 'true', 'anime_status': args, 'types': kind}
                answer = f"<b>Сборка \"{qw}\" по статусу \"{args}\":</b>"
            if type == 2:
                data = {'limit': limit,'with_page_links': 'true', 'anime_studios': args, 'types': kind}
                answer = f"<b>Сборка \"{qw}\" от студии \"{args}\":</b>"
            if type == 1:
                data = {'limit': limit,'with_page_links': 'true', 'year': args, 'types': kind}
                answer = f"<b>Сборка \"{qw}\" по \"{args}\" году:</b>"
            if type == 7 or type == 8:
                if type == 7:
                    answer = f"<b>Сборка \"{qw}\" по названию \"{args}\":</b>"
                    data = {'title': args, 'with_page_links': 'true', 'types': kind}
                if type == 8:
                    data = {'with_page_links': 'true', 'title': args, 'full_match': 'true', 'types': kind}
                    answer = f"<b>Полная инфа по {qws} \"{args}\":</b>"
                r = requests.post('https://kodikapi.com/search?token=8ebf915587af48d001d33127ae55dcb3&with_episodes=true&with_material_data=true', data=data).json()
            else:
                r = requests.post('https://kodikapi.com/list?token=8ebf915587af48d001d33127ae55dcb3&with_episodes=true&with_material_data=tru', data=data).json()
            if type == 8:
                i = r["results"][0]
                m = i["material_data"]
                director = ''
                studio = ''
                try:
                    for directors in m["directors"]:
                        director += f"{directors}, "
                except:
                    director = 'неизвестен.'
                if k == 1 or k == 2:
                    try:
                        for studios in m["anime_studios"]:
                            studio += f"{studios}, "
                    except:
                        studio = 'неизвестна.'
                try:
                    pic = requests.get(m["poster_url"])
                    pic.raw.decode_content = True
                    img = Image.open(io.BytesIO(pic.content)).convert("RGBA")
                    out = io.BytesIO()
                    out.name = "outsider.png"
                    img.save(out)
                    piccer = out.getvalue()
                except:
                    pic = requests.get('https://i.stack.imgur.com/ymxwK.png')
                    pic.raw.decode_content = True
                    img = Image.open(io.BytesIO(pic.content)).convert("RGBA")
                    out = io.BytesIO()
                    out.name = "outsider.png"
                    img.save(out)
                    piccer = out.getvalue()
                try:
                    year = m["year"]
                except:
                    year = 'Неизвестен.'
                try:
                    desc = m["description"]
                except:
                    desc = 'Нет.'
                try:
                    tagline = m["tagline"]
                except:
                    tagline = "Нет."
                try:
                    status = m["anime_status"]
                except:
                    status = 'Неизвестен.'
                try:
                    anikind = m["anime_kind"]
                except:
                    anikind = 'Неизвестен.'
                try:
                    t = m["title_en"]
                except:
                    t = "Неизвестно."
                if k == 1 or k == 2:
                    s += (f'<b>Название:</b> {i["title"]}\n'
                          f'<b>Ориг-название:</b> {t}\n'
                          f'<b>Рейтинг:</b> {m["shikimori_rating"]}\n'
                          f'<b>Голосов:</b> {m["shikimori_votes"]}\n'
                          f'<b>Режиссер</b>: {director}\nCтудия: {studio}\n'
                          f'<b>Год</b>: {year}\nСтатус: {status}\n'
                          f'<b>Тип</b>: {anikind}\n\n'
                          f'<b><a href="{i["link"]}">Ссылка для просмотра</a></b>\n\n\n'
                          f'<b>Описание:</b> {desc}')
                elif k == 3 or k == 4 or k == 5 or k == 6:
                    s += (f'<b>Название:</b> {i["title"]}\n'
                          f'<b>Ориг-название:</b> {t}\n'
                          f'<b>Режиссер:</b> {director}\n'
                          f'<b>Год:</b> {year}\n'
                          f'<b>Cлоган:</b> {tagline}\n\n'
                          f'<b><a href="{i["link"]}">Ссылка для просмотра</a></b>\n\n\n'
                          f'<b>Описание:</b> {desc}')
                info = ''.join(s)
            else:
                for i in r["results"]:
                    n += 1
                    tr = i["translation"]
                    s += f'<b>{n})</b> <a href="{i["link"]}">{i["title"]}</a> <b>| Озвучка:</b> {tr["title"]}\n'
                    info = ''.join(s)
            if type == 8:
                caption = f"{answer}\n\n{info}"
                try:
                    await event.client.send_file(event.to_id, piccer, caption=caption)
                    await event.delete()
                except:
                    await event.edit(f"{answer}\n\n{info}\n\n\n<b>Не получилось загрузить изображение из за слишком длинного описания.</b>")
            else:
                if info:
                    try:
                        await event.edit(f"{answer}\n\n{info}")
                    except:
                        return await event.edit("<b>Слишком большой массив выводимых данных.</b>")
                else:
                    return await event.edit(f"<b>По заданному параментру <b>'{args}'</b> не было ни одного тайтла, слитыш.</b>")
        except KeyError:
            return await event.edit('<b>Неправильный ввод, смотри</b> <code>.kodik help</code><b>.</b>')