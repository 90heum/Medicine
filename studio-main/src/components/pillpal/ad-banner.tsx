"use client";

import Image from "next/image";

export function AdBanner() {
    return (
        <a
            href="http://blog.naver.com/handory"
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full h-[350px] relative rounded-lg overflow-hidden border"
        >
            <Image
                src="/ADbanner.png"
                alt="Advertisement"
                fill
                className="object-fill"
            />
        </a>
    );
}
