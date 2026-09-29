import { describe, expect, it } from "vitest";

import { parseVideoName } from "./video-name";

describe("parseVideoName", () => {
  it("要件の実例を解釈する", () => {
    const parsed = parseVideoName("00004929_2409141309_NF.MP4");
    expect(parsed?.timestamp.equals(Temporal.Instant.from("2024-09-14T13:09:00+09:00"))).toBe(true);
    expect(parsed?.eventType).toBe("normal");
    expect(parsed?.direction).toBe("front");
  });

  it("G は gravitational、S は switch、R は rear", () => {
    expect(parseVideoName("00000001_2312211852_GR.MP4")).toMatchObject({ eventType: "gravitational", direction: "rear" });
    expect(parseVideoName("00000001_2312301515_SF.MP4")).toMatchObject({ eventType: "switch", direction: "front" });
  });

  it("小文字の拡張子とコードも受け付ける", () => {
    expect(parseVideoName("00000001_2312211852_gr.mp4")).toMatchObject({ eventType: "gravitational", direction: "rear" });
  });

  it("規則に合わない名前は undefined", () => {
    expect(parseVideoName("00000001_2312211852_XF.MP4")).toBeUndefined();
    expect(parseVideoName("20231221-1852F.mp4")).toBeUndefined();
    expect(parseVideoName("00000001_2312211852_NF.MP4.part")).toBeUndefined();
  });

  it("存在しない日付は例外", () => {
    expect(() => parseVideoName("00000001_2313011852_NF.MP4")).toThrow(RangeError);
  });
});
